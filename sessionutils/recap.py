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

    @recap.command()
    async def stop(self, ctx):
        """Stop collecting messages"""
        self.collecting = False
        await ctx.send("Stopped collecting messages")

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
        full_message =f"{header}\n{message}"
        await target_channel.send(full_message)
        await ctx.send("Announcement posted to Town Crier")

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
