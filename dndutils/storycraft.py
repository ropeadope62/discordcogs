import asyncio
from redbot.core import commands, checks
from datetime import datetime, timedelta
import json
from typing import List
import os
from .story_ai.story_ai import StoryCraft_AI
import glob
import discord


from discord import Embed

story_ai = StoryCraft_AI()


class StoryCraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = False  # Still to add global enable/disable command
        self.timer = 5  # Placeholder for timer
        self.temp_messages = []
        self.collecting = False
        self.last_story = None
        self.announce_channel = self.bot.get_channel(
            1157129358406856704
        )  # 1154282874401456149 Test channel

    def read_story(self):
        """Reads the story.json file and returns the data"""

        with open(".\\story.json", "r") as file:
            data = json.load(file)
            return data["story"]

    def update_story(self, data_to_update):
        """Updates the story.json file with the new data"""
        with open(".\\story.json", "w") as file:
            json.dump(data_to_update, file)

    def get_latest_story(self):
        """Returns the path of the latest story file based on the creation time."""

        return max(glob.glob("story_*.txt"), key=os.path.getctime)

    def get_formatted_date_from_filename(file_name):
        """Step 1: Extract date-time string from file name"""
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

    async def send_paginated_embed(
        self, ctx, target_channel, content_list, summary, *, announcement_title
    ):
        """For sending paginated embeds to be used with the story announce command."""
        # await ctx.send(f"Announce Channel: {self.announce_channel}")  # Debug line
        # await ctx.send(
        #    f"Debug: Entered send_paginated_embed. Target: {self.announce_channel}, Content Length: {len(content_list)}"
        # )
        target_channel = self.announce_channel
        page = 0
        embed = discord.Embed(
            title=f"{announcement_title} - {datetime.now().strftime('%Y-%m-%d')}\n",
            description=f"*{summary}*",
            color=0xEEE657,
        )
        embed.add_field(name="The full story...", value=content_list[page][:1024])
        embed.set_author(name="Town Crier")
        embed.set_thumbnail(url="https://i.imgur.com/3FaAUZI.png")
        embed.set_footer(text=f"Feathered Crickets 2023 | Page {page+1}")

        message = await target_channel.send(embed=embed)

        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in {"◀️", "▶️"}

        while True:
            try:
                reaction, user = await ctx.bot.wait_for(
                    "reaction_add", timeout=60, check=check
                )

                if str(reaction.emoji) == "▶️" and page < len(content_list) - 1:
                    page += 1
                    new_field_value = content_list[page][
                        :1024
                    ]  # Update the value of the field
                    embed.set_field_at(
                        0, name="The full story...", value=new_field_value
                    )  # Update the first field
                    await message.edit(embed=embed)

                elif str(reaction.emoji) == "◀️" and page > 0:
                    page -= 1
                    new_field_value = content_list[page][
                        :1024
                    ]  # Update the value of the field
                    embed.set_field_at(
                        0, name="The full story...", value=new_field_value
                    )  # Update the first field
                    await message.edit(embed=embed)

                await message.remove_reaction(reaction, user)

            except asyncio.TimeoutError:
                break

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
        self.collecting = False
        collected_text = " ".join(self.temp_messages)
        file_name = f"story_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        with open(file_name, "w") as file:
            file.write(collected_text)
        await ctx.send(f"Stopped collecting messages. Story saved to {file_name}.")
        self.temp_messages = []

    @storycraft.command()
    async def generate(
        self,
        ctx,
        temperature: float = 0.3,
        frequency_penalty: float = 0.5,
        presence_penalty: float = 0.5,
    ):
        """Send the latest session to OpenAI to generate a story.\n
        Usage: >storycraft generate"""

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
    async def conversation(self, ctx):
        """Retrieve the current OpenAI conversation history.\n
        Usage: >storycraft history"""
        conversation_history = story_ai.conversation_history
        await ctx.send(conversation_history)

    async def get_summary(self, ctx):
        """Prompt the user to summarize the story into one line."""
        last_story = self.last_story
        summary_prompt = [
            {
                "role": "user",
                "content": f"Summarize the following story into one line: {last_story}",
            }
        ]
        summary = story_ai.summarize_story_title(
            last_story=last_story, summary_prompt=summary_prompt
        )
        return summary

    @storycraft.command()
    async def announce(self, ctx, *, announcement_title):
        """Announce to the Town Crier channel.\n
        Usage: >storycraft announce <message>"""
        # send the message in the town crier channel
        last_story = self.last_story
        target_channel = self.announce_channel
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

        await ctx.send("Announcement posted to Town Crier")

    @storycraft.command()
    async def help(self, ctx):
        """Displays the StoryCraft Help Menu in an embed."""
        # make an embed
        embed = discord.Embed(
            title="StoryCraft Help Menu",
            description="StoryCraft will record a several messages and write them into a story in the style of high fantasy. Commands for StoryCraft",
            color=0xEEE657,
        )

        # set the fields of the embed
        embed.add_field(
            name=">storycraft start",
            value="Start collecting messages for the story",
            inline=False,
        )
        embed.add_field(
            name=">storycraft stop",
            value="Stop collecting messages for the story",
            inline=False,
        )
        embed.add_field(
            name=">storycraft generate",
            value="Send the latest session to OpenAI for story generation",
            inline=False,
        )
        embed.add_field(
            name=">storycraft announce",
            value="Announce the latest story to the Town Crier",
            inline=False,
        )
        embed.add_field(
            name=">storycraft edit",
            value="Edit the latest story",
            inline=False,
        )
        embed.add_field(
            name=">storycraft history",
            value="Retrieve the current OpenAI conversation history",
            inline=False,
        )

        await ctx.send(embed=embed)

    @storycraft.command()
    async def history(self, ctx):
        """Returns a list of all session files."""
        embed = discord.Embed(
            title="Previous Stories",
            description="Here's a list of previous sessions:",
            color=0xEEE657,
        )
        for file in glob.glob("session_*.txt"):
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

    @commands.Cog.listener("on_message")
    async def on_message_listener(self, message):
        """Listens for messages and appends the content of non-bot messages to the temporary messages list if collecting is enabled."""

        if message.author.bot:
            return

        if self.collecting:
            self.temp_messages.append(message.content)


def setup(bot):
    bot.add_cog(StoryCraft(bot))
