import asyncio
from redbot.core import commands, checks
from datetime import datetime, timedelta
import json


class FlashDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = False
        self.timer = 5
        self.bot.loop.create_task(self.delete_messages())

    def read_channel_ids(self):
        with open(".\\flashdelete_channels.json", "r") as file:
            data = json.load(file)
            return data["channel_ids"]

    def update_channel_ids(self):
        with open(".\\flashdelete_channels.json", "w") as file:
            json.dump(file)

    @commands.group()
    @checks.admin_or_permissions(manage_messages=True)
    async def flashdelete(self, ctx):
        """FlashDelete - Gone, in a #Flash!"""

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

    async def flashdelete_task(self):
        while True:
            if self.enabled:
                await self.delete_messages()
            await asyncio.sleep(self.timer * 60)

    async def delete_messages(self):
        deleted_messages_count = 0
        # for channel_id in self.read_channel_ids(): For use with json, we will use the hardcoded list for now
        for channel_id in [1020933443179253800, 1130587895665807371]:
            channel = self.bot.get_channel(channel_id)
            if channel:
                messages_to_delete = []
                async for message in channel.history(limit=None):
                    time_diff = datetime.now().astimezone() - message.created_at
                    if (
                        time_diff > timedelta(minutes=self.timer)
                        and time_diff < timedelta(days=14)
                        and len(message.attachments) > 0
                    ):
                        messages_to_delete.append(message)
                        if len(messages_to_delete) >= 100:
                            await channel.delete_messages(messages_to_delete)
                            deleted_messages_count += len(messages_to_delete)
                            messages_to_delete = []
                if messages_to_delete:
                    await channel.delete_messages(messages_to_delete)
                    deleted_messages_count += len(messages_to_delete)
                print(
                    "FlashDelete Cleanup Completed: Deleted {deleted_messages_count} messages."
                )
                await channel.send(
                    f"FlashDelete Cleanup Completed: Deleted {deleted_messages_count} messages."
                )
