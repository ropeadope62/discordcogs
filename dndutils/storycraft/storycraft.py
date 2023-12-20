import asyncio
from datetime import datetime, timedelta
import json
from typing import List
import os
import glob
import discord

from redbot.core import commands, checks, app_commands, Config
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils import menus
from redbot.core.utils.menus import DEFAULT_CONTROLS
from interactions.ext.paginators import Paginator
from .story_ai.story_ai import StoryCraft_AI
from .story_maps.story_maps import StoryMaps

from discord import (
    Embed,
    Button,
    Interaction,
    Message,
    ui,
    InteractionResponse,
    ButtonStyle,
)

story_ai = StoryCraft_AI()
story_map = StoryMaps()


class ConfirmButton(ui.Button["ConfirmationView"]):
    def __init__(self, label: str, custom_id: str):
        super().__init__(style=1, label=label, custom_id=custom_id)

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        self.view.value = self.custom_id
        self.view.stop()


class ConfirmationView(ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @ui.button(label="Yes", style=ButtonStyle.primary, custom_id="yes_generate")
    async def yes_button(self, interaction: Interaction, button: ui.Button):
        self.value = "yes_generate"
        await interaction.response.defer()
        self.stop()
        await self.generate.invoke(interaction)
        await interaction.followup.edit_message(interaction.message.id, view=None)

    @ui.button(label="No", style=ButtonStyle.danger, custom_id="no_generate")
    async def no_button(self, interaction: Interaction, button: ui.Button):
        self.value = "no_generate"
        await interaction.response.defer()
        self.stop()
        await interaction.followup.edit_message(interaction.message.id, view=None)


class StoryCraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_messages = []
        self.collecting = False
        self.last_story = None
        self.announce_channel_id = 1157129358406856704  # Should be in a config
        self.announce_channel = self.bot.get_channel(self.announce_channel_id)
        self.party_location = None
        self.story_entries = 0
        self.config = Config.get_conf(self, identifier=7778465121547)
        default_guild = {"stories": {}}
        self.config.register_guild(**default_guild)

    async def read_json_file(self, file_name):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._read_json_file, file_name)

    def _read_json_file(self, file_name):
        with open(file_name, "r") as file:
            return json.load(file)

    async def write_json_file(self, file_name, new_story):
        try:
            with open(file_name, "r") as f:
                existing_history = json.load(f)
        except FileNotFoundError:
            existing_history = {"stories": []}  # Initialize if file doesn't exist

        # Initialize 'stories' if not present
        if "stories" not in existing_history:
            existing_history["stories"] = []

        existing_history["stories"].append(new_story)

        with open(file_name, "w") as f:
            json.dump(existing_history, f, indent=4)

    def get_latest_story(self):
        """Returns the path of the latest story file based on the creation time."""

        return max(glob.glob("story_*.txt"), key=os.path.getctime)

    def get_formatted_date_from_filename(file_name):
        """Extract the date from the file name and format it."""
        date_str = file_name.split("_")[1].split(".")[
            0
        ]  # Assuming "story_" prefix and ".txt" suffix
        dt = datetime.strptime(date_str, "%Y%m%d%H%M%S")
        day = int(dt.strftime("%d"))
        suffix = (
            "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        )
        formatted_date = f"{day}{suffix} of {dt.strftime('%B')}, {dt.year}"
        return formatted_date

    async def send_story_chunks(ctx, content: str, chunk_size: int = 2000):
        """Splits the content into chunks that fit within Discord's 2000-character limit for messages."""
        if len(content) <= chunk_size:
            await ctx.send(content)
            return

        lines = content.split("\n")
        message = ""
        for line in lines:
            if len(message) + len(line) + 1 > chunk_size:
                await ctx.send(message)
                message = ""

            message += line + "\n"

        if message:
            await ctx.send(message)

    def split_chunks_for_embed(self, last_story, chunk_size=1024):
        """Splits the content into chunks that fit within Discord's 1024-character limit for embed fields."""
        chunks = []
        for i in range(0, len(last_story), chunk_size):
            chunks.append(last_story[i : i + chunk_size])
        return chunks

    async def send_paginated_embed(self, ctx, target_channel, content_list, summary, *, announcement_title):
        """For sending paginated embeds to be used with the story announce command."""
        embeds = []
        for page, content in enumerate(content_list, start=1):
            embed = Embed(
                title=f"{announcement_title} - {datetime.now().strftime('%Y-%m-%d')}\n",
                description=f"*{summary}*\n\n{content[:1024]}",
                color=0x8E7CC3
            )
            embed.set_author(name="StoryCraft")
            embed.set_thumbnail(url="https://i.imgur.com/3FaAUZI.png")
            embed.set_footer(text=f"{announcement_title} - Page {page}")
            embeds.append(embed)

        await menus.menu(ctx, embeds, DEFAULT_CONTROLS, message=None, page=0, timeout=3600)

        async def interaction_paginator(self, ctx, last_story):
            bot = self.bot 
            paginator = Paginator.create_from_string(bot, last_story, page_size=1000)
            await paginator.send(ctx)            

    @commands.group()
    @checks.admin_or_permissions(manage_messages=True)
    async def storycraft(self, ctx):
        """Convert DND game session notes into a high fantasy story with GPT4.\n
        Usage: >storycraft <command>\n
        To get started, use >storycraft help"""
        pass

    @storycraft.command()
    async def start(self, ctx):
        """Start collecting messages.\n
        Usage: >storycraft start
        """
        self.collecting = True
        await ctx.send("Started collecting messages for the story.")

    @storycraft.command()
    async def stop(self, ctx):
        """Stop collecting messages, join them into one string and save to a txt file.\n
        Usage: >story stop"""
        collected_text = " ".join(self.temp_messages)
        file_name = f"story_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        with open(file_name, "w") as file:
            file.write(collected_text)
        await ctx.send(f"Stopped collecting messages. Story saved to {file_name}.")
        self.temp_messages = []
        view = ConfirmationView()
        self.collecting = False
        await ctx.send("Do you want to go ahead and generate a story?", view=view)
        await view.wait()

        if view.value == "yes_generate":
            await self.generate.invoke(ctx)

        elif view.value == "no_generate":
            await ctx.send("Story generation cancelled.")

    @storycraft.command()
    async def generate(
        self,
        ctx,
        temperature: float = 0.3,
        frequency_penalty: float = 0.5,
        presence_penalty: float = 0.5,
    ):
        """Send the latest session to OpenAI to generate a story.\n
        Usage: >storycraft generate\n Optional Parameters: \n temperature: (default 0.3) \n frequency_penalty: (default 0.5) \n presence_penalty: (default 0.5) \n Usage with custom parameters: >storycraft generate 0.5 0.5 0.5
        """

        adjustment_params = {
            "temperature": temperature,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
        }
        await ctx.send("Generating Story...")
        file_name = self.get_latest_story()
        with open(file_name, "r") as file:
            messages = file.read()
            response = story_ai.session_to_story_gpt4(messages, adjustment_params)
            self.last_story = response
            story_ai.set_last_story(response)
            await StoryCraft.send_story_chunks(ctx, response)
            await self.write_json_file("story_history.json", {"story": self.last_story})

        await ctx.send(
            "\n\nAre you pleased with this story? Use >storycraft save to save it or >storycraft edit <changes> to make changes."
        )

    @storycraft.command()
    async def edit(self, ctx, last_story, *, edit_prompt: str):
        """Make changes to an existing story.\n
        Usage: >storycraft edit <message>\n
        This will modify the previously generated story."""
        last_story = self.last_story
        await ctx.send("Processing New Story...")
        response = story_ai.edit_story(last_story, edit_prompt)
        await StoryCraft.send_story_chunks(ctx, response)

    @storycraft.command()
    async def conversation_history(self, ctx):
        """Retrieve the current OpenAI conversation history.\n
        Usage: >storycraft history"""
        conv_history = await self.read_json_file("story_history.json")
        await ctx.send(conv_history)

    async def get_summary(self, ctx):
        """Prompt the user to summarize the story into one line."""
        last_story = self.last_story
        summary_prompt = [
            {
                "role": "user",
                "content": f"Summarize the following story into one line: {last_story}",
            }
        ]
        return story_ai.summarize_story_title(
            last_story=last_story, summary_prompt=summary_prompt
        )

    @storycraft.command()
    async def announce(self, ctx, *, announcement_title):
        """Announce to the StoryCraft channel.\n
        Usage: >storycraft announce <message>"""
        # send the paginated embed to the StoryCraft channel
        last_story = self.last_story
        target_channel = self.bot.get_channel(1154282874401456149)
        summary = await self.get_summary(ctx)
        if target_channel is None:
            await ctx.send("Channel not found")
            return
        # make a discord embed
        story_chunks = self.split_chunks_for_embed(last_story)

        await self.send_paginated_embed(
            ctx,
            target_channel,
            story_chunks,
            summary,
            announcement_title=announcement_title,
        )

        await ctx.send("Announcement posted to Story Craft channel")
        
        guild = ctx.guild
        story_data = {
            "summary": summary,
            "content": last_story
        }
        async with self.config.guild(guild).stories() as stories:
            stories[announcement_title] = story_data

    @storycraft.command()
    async def getstory(self, ctx, *, title):
        """Retrieve a story by its title."""
        guild = ctx.guild
        target_channel = self.bot.get_channel(1154282874401456149)
        stories = await self.config.guild(guild).stories()
        story_data = stories.get(title)
        if story_data:
            summary = story_data["summary"]
            content = story_data["content"]
            story_chunks = self.split_chunks_for_embed(content)
            
        await self.send_paginated_embed(
            ctx,
            target_channel,
            story_chunks,
            summary,
            announcement_title=summary,
        )

    @storycraft.command()
    async def announce_test(self, ctx, *, announcement_title):
        """Announce to the StoryCraft channel - Test Server\n
        Usage: >storycraft announce <message>"""
        # send the paginated embed to the StoryCraft channel
        last_story = self.last_story
        target_channel = self.bot.get_channel(1157129358406856704)
        summary = await self.get_summary(ctx)
        story_chunks = self.split_chunks_for_embed(last_story)

        await self.send_paginated_embed(
            ctx,
            target_channel,
            story_chunks,
            summary,
            announcement_title=announcement_title,
        )

        await ctx.send("Announcement posted to Story Craft channel")

    @storycraft.command()
    async def help(self, ctx):
        """Displays the StoryCraft Help Menu in an embed."""

        # Create the embed

        embed = discord.Embed(
            title="StoryCraft Help Menu",
            description="StoryCraft will record dnd session notes as user messages and write them into a story in the style of high fantasy.",
            color=0x8E7CC3,
        )

        # set the fields of the embed
        embed.set_thumbnail(url="https://iili.io/J28Etst.png")
        embed.add_field(
            name=">storycraft start",
            value="Start collecting messages for the story.\n Usage: >storycraft start",
            inline=False,
        )
        embed.add_field(
            name=">storycraft stop",
            value="Stop collecting messages for the story.\n Usage: >storycraft stop",
            inline=False,
        )
        embed.add_field(
            name=">storycraft generate",
            value="Send the latest session to OpenAI for story generation. \n Usage: >storycraft generate \n Optional Parameters: \n temperature: (default 0.3) \n frequency_penalty: (default 0.5) \n presence_penalty: (default 0.5) \n Usage with custom parameters: >storycraft generate 0.5 0.5 0.5 ",
            inline=False,
        )
        embed.add_field(
            name=">storycraft announce",
            value="Announce the latest story to the Town Crier.\n Usage: >storycraft announce <title>",
            inline=False,
        )
        embed.add_field(
            name=">storycraft edit",
            value="Edit the latest story. \n Usage: >storycraft edit <user message>",
            inline=False,
        )
        embed.add_field(
            name=">storycraft showmap",
            value="Show the map of a city, town or region. \n Usage: >storycraft showmap <location> \n >storycraft showmap locations, for a list of locations.",
            inline=False,
        )

        await ctx.send(embed=embed)

    @storycraft.command()
    async def history(self, ctx):
        """Returns a list of all session files."""
        data = await self.read_json_file("story_history.json")
        embed = discord.Embed(
            title="Previous Stories",
            description="Here's a list of previous stories:",
            color=0x8E7CC3,
        )
        for file in glob.glob("story_*.txt"):
            embed.add_field(
                name=file,
                value=StoryCraft.get_formatted_date_from_filename(file),
                inline=False,
            )

        await ctx.send(embed=embed)

    @storycraft.command()
    async def get(self, ctx, filename):
        """get a session based on file in glob.glob("session_*.txt")"""
        if filename is None:
            filename = self.get_latest_session()
            await ctx.send(f"Retrieving latest session: {filename}")
        else:
            await ctx.send(f"Retrieving session: {filename}")
            with open(filename, "r") as file:
                messages = file.read()
            await ctx.send(messages)

    @storycraft.command()
    async def channel(self, ctx, target_channel: int):
        """Set the channel for the storycraft announcements.\n Usage: >storycraft channel <channel_id>"""
        target_channel_obj = self.bot.get_channel(target_channel)
        if target_channel_obj is None:
            await ctx.send(f"No channel found with ID {target_channel}.")
            return
        self.announce_channel = target_channel_obj
        await ctx.send(
            f"Announcements will be posted to {self.announce_channel.mention}"
        )

    @storycraft.command()
    async def showmap(self, ctx, *, location: str):
        """Show the current map location."""
        await story_map.show_map(ctx, location.lower())

    @commands.Cog.listener("on_message")
    async def on_message_listener(self, message):
        """Listens for messages and appends the content of non-bot messages to the temporary messages list if collecting is enabled."""

        if message.author.bot:
            return

        if self.collecting and not message.content.startswith(">storycraft"):
            self.temp_messages.append(message.content)


def setup(bot):
    bot.add_cog(StoryCraft(bot))
