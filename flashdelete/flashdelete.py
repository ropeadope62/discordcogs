import discord
import asyncio
from redbot.core import commands
from datetime import datetime, timedelta
from redbot.core import commands, checks
from time import sleep
import json


class FlashDelete(commands.Cog):
    """FlashDelete - Gone in a #Flash!"""

    def __init__(self, bot):
        self.bot = bot
        self.enabled = False
        self.timer = 5

    @commands.group()
    @checks.admin_or_permissions(manage_messages=True)
    async def flashdelete(self, ctx):
        """Root Command for Flash Delete Configuration"""

    @flashdelete.command()
    async def status(self, ctx, status: str):
        """Enable or Disable Flash Delete"""
        if status.lower() == "enable":
            self.enabled = True
            await ctx.send("Flash Delete Enabled")
        elif status.lower() == "disable":
            self.enabled = False
            await ctx.send("Flash Delete Disabled")
        else:
            await ctx.send("Invalid Status")

    @flashdelete.command()
    async def timer(self, ctx, timer: int):
        """Set the timer for Flash Delete"""
        try:
            self.timer = timer
            await ctx.send(f"Flash Delete Timer set to {timer} minutes")
        except Exception:
            await ctx.send("Invalid timer value")

    @flashdelete.command()
    async def now(self, ctx):
        """Run Flash Delete Now"""
        await self.delete_messages()

    async def delete_messages(self):
        while True:
            if self.enabled:
                deleted_messages_count = 0
                for channel_id in self.read_channel_ids():
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        messages_to_delete = []
                        async for message in channel.history(limit=None):
                            if (
                                datetime.now() - message.created_at
                                > timedelta(minutes=self.timer)
                                and len(message.attachments) > 0
                            ):
                                messages_to_delete.append(message)
                                if len(messages_to_delete) >= 100:
                                    await channel.delete_messages(messages_to_delete)
                                    deleted_messages_count += len(messages_to_delete)
                                    messages_to_delete = []
                        if (
                            messages_to_delete
                        ):  # if there are leftover messages less than 100
                            await channel.delete_messages(messages_to_delete)
                            deleted_messages_count += len(messages_to_delete)
                        await channel.send(
                            f"FlashDelete Cleanup Completed: Deleted {deleted_messages_count} messages."
                        )
            await asyncio.sleep(self.timer * 60)

    def read_channel_ids(self):
        with open("flashdelete_channels.json", "r") as file:
            data = json.load(file)
            return data["channel_ids"]