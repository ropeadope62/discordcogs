import asyncio
from redbot.core import commands, checks
from datetime import datetime, timedelta
import json
from typing import List


class Recap(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = False
        self.timer = 5
        self.temp_messages = []
        self.collecting = False
        self.end_word = "CONCLUDED"

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
    async def collect(self, ctx, end: str = "CONCLUDED"):
        """Collect messages for recap"""
        self.end_word = end
        self.collecting = True
        await ctx.send("Collecting messages since last Recap")

    @commands.Cog.listener("on_message")
    async def on_message_listener(self, message):
        if message.author.bot:
            return

        if self.collecting:
            self.temp_messages.append(message.content)
            if self.end_word in message.content:
                self.collecting = False
                collected_text = " ".join(self.temp_messages)
                await message.channel.send(f"Recap:\n{collected_text}")
                self.temp_messages = []
