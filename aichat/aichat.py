import discord
from redbot.core import commands
from typing import List


class AIChatSomething(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """AI Game"""
        pre_processed = f"{super().format_help_for_context(ctx)}\n\n"
        return f"{pre_processed}\n\nCog Version: 1.0.0"

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete"""
        return

    async def get_user_messages(self, ctx, member: discord.Member):
        """Get all messages from a user"""
        channel = ctx.channel
        user_messages = []
        async for message in channel.history(limit=50):
            if message.author == member:
                user_messages.append(message.content)
        return user_messages

    @commands.command()
    async def aichat(self, ctx, member: discord.Member):
        """Member chat history"""
        await ctx.send("member chat history")
        user_messages = await self.get_user_messages(ctx, member)
        await ctx.send(user_messages)


# 
number = "1.5"
#convert number to a float, then an int and round to 1 decimal place
rounded = round(int(float(number)), 1)
#convert number to an int
integer = int(number)
#convert number to a string

#round number to 1 decimal place
rounded = round(number, 1)