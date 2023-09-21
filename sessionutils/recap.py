import asyncio
from redbot.core import commands, checks
from datetime import datetime, timedelta
import json
from typing import List
import os
from openai import OpenAI


class Recap(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = False
        self.timer = 5
        self.temp_messages = []
        self.collecting = False
        self.end_word = "CONCLUDED"
        openai = OpenAI()

    def read_recap(self):
        with open(".\\recap.json", "r") as file:
            data = json.load(file)
            return data["recap"]

    def update_recap(self, data_to_update):
        with open(".\\recap.json", "w") as file:
            json.dump(data_to_update, file)

    @commands.group()
    @checks.admin_or_permissions(manage_messages=True)
    async def recap(self, ctx):
        pass

    @recap.command()
    async def collect(self, ctx):
        """Collect messages for recap."""
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
        await ctx.send("Generating recap...")
        file_name = self.get_latest_file_name()
        with open(file_name, "r") as file:
            prompt = file.read()
            response = self.openai.recap_to_story(prompt)
            await ctx.send(response)
        # os.remove(file_name)

    @recap.command()
    async def announce(self, ctx, message: str):
        """Announce to the town crier"""
        await ctx.send(message)
        # send the message in a specific channel
        target_channel = self.bot.get_channel(1154282874401456149)
        if target_channel is None:
            await ctx.send("Channel not found")
            return
        header = f"__**DND Session Recap__**"
        full_message = f"{header}\n{message}"
        await target_channel.send(full_message)
        await ctx.send("Announcement posted to Town Crier")

    @commands.Cog.listener("on_message")
    async def on_message_listener(self, message):
        if message.author.bot:
            return

        if self.collecting:
            self.temp_messages.append(message.content)