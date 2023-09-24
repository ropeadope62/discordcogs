import asyncio
from redbot.core import commands, checks
from datetime import datetime, timedelta
import json
from typing import List
import os
from .recap_ai.recap_ai import OpenAI
import glob
import discord


openai = OpenAI()
openai.api_key = os.getenv("OPENAI_API_KEY")


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

    @commands.group()
    @checks.admin_or_permissions(manage_messages=True)
    async def recap(self, ctx):
        """Record user messages and turn it into a story with GPT4. This is an empty command for grouping purposes."""
        pass

    @recap.command()
    async def start(self, ctx):
        """Start collecting messages for recap."""
        self.collecting = True
        await ctx.send("Started collecting messages for the recap.")

    @recap.command()
    async def stop(self, ctx):
        """Stop collecting messages."""
        self.collecting = False
        collected_text = " ".join(self.temp_messages)
        file_name = f"recap_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        with open(file_name, "w") as file:
            file.write(collected_text)
        await ctx.send(f"Stopped collecting messages. Recap saved to {file_name}.")
        self.temp_messages = []

    @recap.command()
    async def generate(self, ctx):
        """Send the latest recap to OpenAI for story generation."""
        await ctx.send("Generating recap...")
        file_name = self.get_latest_recap()
        with open(file_name, "r") as file:
            prompt = file.read()
            response = openai.recap_to_story_gpt4(prompt)
            await ctx.send(response)

    @recap.command()
    async def add(self, ctx, message: str):
        await ctx.send("Adding to recap...")
        response = openai.add_to_recap(message)
        await ctx.send(response)

    @recap.command()
    async def history(self, ctx):
        conversation_history = openai.read_conversation_history()
        await ctx.sent(conversation_history)

    @recap.command()
    async def announce(self, ctx, message: str):
        """Announce to the Town Crier channel."""
        # send the message in the town crier channel
        target_channel = self.bot.get_channel(1154282874401456149)
        if target_channel is None:
            await ctx.send("Channel not found")
            return
        header = f"Recap for {datetime.now().strftime('%Y-%m-%d')}"
        # make a discord embed
        embed = discord.Embed(title="Recap", description=message, color=0xEEE657)
        embed.add_field(name="Hello", value=header, inline=False)
        embed.add_field(name="Message", value=message, inline=False)
        embed.set_author(name="Town Crier")
        embed.set_thumbnail(url="https://imgur.com/a/yid0sL7")
        embed.set_footer(text="Town Crier")
        await ctx.send(embed)

        await target_channel.send(embed)
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

        await ctx.send(embed=embed)

    @commands.Cog.listener("on_message")
    async def on_message_listener(self, message):
        """Listens for messages and appends the content of non-bot messages to the temporary messages list if collecting is enabled."""

        if message.author.bot:
            return

        if self.collecting:
            self.temp_messages.append(message.content)


def setup(bot):
    bot.add_cog(Recap(bot))
