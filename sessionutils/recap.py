import asyncio
from redbot.core import commands, checks
from datetime import datetime, timedelta
import json
from typing import List
import os
from .recap_ai.recap_ai import Recap_AI
import glob
import discord


from discord import Embed

recap_ai = Recap_AI()


class Recap(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = False  # Still to add global enable/disable command
        self.timer = 5  # Placeholder for timer
        self.temp_messages = []
        self.collecting = False

    def read_recap(self):
        with open(".\\recap.json", "r") as file:
            data = json.load(file)
            return data["recap"]

    def update_recap(self, data_to_update):
        with open(".\\recap.json", "w") as file:
            json.dump(data_to_update, file)

    def get_latest_recap(self):
        """Returns the path of the latest recap file based on the creation time."""

        return max(glob.glob("recap_*.txt"), key=os.path.getctime)

    def get_formatted_date_from_filename(file_name):
        """Step 1: Extract date-time string from file name"""
        date_str = file_name.split("_")[1].split(".")[
            0
        ]  # Assuming "recap_" prefix and ".txt" suffix
        dt = datetime.strptime(date_str, "%Y%m%d%H%M%S")
        day = int(dt.strftime("%d"))
        suffix = (
            "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        )
        formatted_date = f"{day}{suffix} of {dt.strftime('%B')}, {dt.year}"
        return formatted_date

    async def send_story_chunks(ctx, content: str, chunk_size: int = 2000):
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

    @commands.group()
    @checks.admin_or_permissions(manage_messages=True)
    async def recap(self, ctx):
        """Record user messages and turn it into a story with GPT4. This is an empty command for grouping purposes."""
        pass

    @recap.command()
    async def start(self, ctx):
        """Start collecting messages.\n
        Usage: >recap start
        """
        self.collecting = True
        await ctx.send("Started collecting messages for the recap.")

    @recap.command()
    async def stop(self, ctx):
        """Stop collecting messages.\n
        Usage: >recap stop"""
        self.collecting = False
        collected_text = " ".join(self.temp_messages)
        file_name = f"recap_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        with open(file_name, "w") as file:
            file.write(collected_text)
        await ctx.send(f"Stopped collecting messages. Recap saved to {file_name}.")
        self.temp_messages = []

    @recap.command()
    async def generate(
        self,
        ctx,
        temperature: float = 0.3,
        frequency_penalty: float = 0.5,
        presence_penalty: float = 0.5,
    ):
        """Send the latest recap to OpenAI to generate a story.\n
        Usage: >recap generate"""
        adjustment_params = {
            "temperature": temperature,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
        }
        await ctx.send("Generating Story...")
        file_name = self.get_latest_recap()
        with open(file_name, "r") as file:
            messages = file.read()
            response = recap_ai.recap_to_story_gpt4(messages, adjustment_params)
            await Recap.send_story_chunks(ctx, response)

    @recap.command()
    async def edit(self, ctx, message: str):
        """Make changes to an existing story.\n
        Usage: >recap edit <message>\n
        This will modify the previously generated story."""
        await ctx.send("Processing New Story...")
        response = recap_ai.edit_story(message)
        await ctx.send(response)

    @recap.command()
    async def conversation(self, ctx):
        """Retrieve the current OpenAI conversation history.\n
        Usage: >recap history"""
        conversation_history = recap_ai.conversation_history
        await ctx.send(conversation_history)

    @recap.command()
    async def announce(self, ctx, message: str):
        """Announce to the Town Crier channel.\n
        Usage: >recap announce <message>"""
        # send the message in the town crier channel
        target_channel = self.bot.get_channel(1154282874401456149)
        if target_channel is None:
            await ctx.send("Channel not found")
            return
        header = f"Recap for {datetime.now().strftime('%Y-%m-%d')}"
        # make a discord embed
        embed = Embed(
            title="Chat-SRD Commands",
            description="Here's a list of available commands:",
            color=0x00FF00,  # Green color
        )
        embed = discord.Embed(
            title=f"Session Recap for {datetime.now().strftime('%Y-%m-%d')}",
            description="The adventure continues...",
            color=0xEEE657,
        )
        embed.add_field(name="Announcement", value=header, inline=False)
        embed.add_field(
            name="The Story So Far...",
            value=f"Recap for {datetime.now().strftime('%Y-%m-%d')} \n Recap for {datetime.now().strftime('%Y-%m-%d')} \n ",
            inline=False,
        )
        embed.set_author(name="Town Crier")
        embed.set_thumbnail(url="https://i.imgur.com/3FaAUZI.png")
        embed.set_footer(text="Feathered Crickets 2023")

        await target_channel.send(embed=embed)
        await ctx.send("Announcement posted to Town Crier")

    @recap.command()
    async def help(self, ctx):
        """Displays the Recap Help Menu in an embed."""
        # make an embed
        embed = discord.Embed(
            title="Recap Help Menu",
            description="Recap will record a several messages and write them into a story in the style of high fantasy. Commands for Recap",
            color=0xEEE657,
        )

        # set the fields of the embed
        embed.add_field(
            name=">recap start",
            value="Start collecting messages for the recap",
            inline=False,
        )
        embed.add_field(
            name=">recap stop",
            value="Stop collecting messages for the recap",
            inline=False,
        )
        embed.add_field(
            name=">recap generate",
            value="Send the latest recap to OpenAI for story generation",
            inline=False,
        )
        embed.add_field(
            name=">recap announce",
            value="Announce the latest recap to the Town Crier",
            inline=False,
        )
        embed.add_field(
            name=">recap edit",
            value="Edit the latest story",
            inline=False,
        )
        embed.add_field(
            name=">recap history",
            value="Retrieve the current OpenAI conversation history",
            inline=False,
        )

        await ctx.send(embed=embed)

    @recap.command()
    async def history(self, ctx):
        """Returns a list of all recap files."""
        embed = discord.Embed(
            title="Previous Recaps",
            description="Here's a list of previous recaps:",
            color=0xEEE657,
        )
        for file in glob.glob("recap_*.txt"):
            embed.add_field(
                name=file,
                value=Recap.get_formatted_date_from_filename(file),
                inline=False,
            )

        await ctx.send(embed=embed)

    @recap.command()
    async def get(self, ctx, filename):
        """get a recap based on file in glob.glob("recap_*.txt")"""
        if filename is None:
            filename = self.get_latest_recap()
            await ctx.send(f"Retrieving latest recap: {filename}")
        else:
            await ctx.send(f"Retrieving recap: {filename}")
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
    bot.add_cog(Recap(bot))
