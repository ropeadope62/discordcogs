import discord
from redbot.core import Config, commands, checks
from redbot.core.bot import Red
from typing import Union
from datetime import timedelta, datetime
from collections import defaultdict
import asyncio

class Notoriety(commands.Cog):
    """User title system for Red DiscordBot"""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=654649844651)
        default_guild = {
            "titles": {'Hobo': None, 'Peasant': None, 'Knight': None, 'Lord': None, 'King': None},
            "nominations": defaultdict(dict),
            "votes": defaultdict(int),
            "nomination_counts": defaultdict(int),
            "nomination_threshold": 1,
            "vote_threshold": 1,
            "duration": 30
        }
        self.config.register_guild(**default_guild)


    
    @commands.group()
    @checks.admin_or_permissions(manage_messages=True)
    async def notoriety(self, ctx):
        """Command for nomination, voting and assignment of user titles"""

    @notoriety.command()
    async def nominate(self, ctx, user: Union[discord.Member, discord.User], title: str):
        """Nominate a user for a title"""
        async with self.config.guild(ctx.guild).nominations() as nominations:
            if nominations.get(title) is None:
                nominations[title] = {}
            
            if user.id not in nominations[title]:
                nominations[title][user.id] = ctx.author.id
                await ctx.send(f"{ctx.author.mention} has nominated {user.mention} for the title: {title}")

                async with self.config.guild(ctx.guild).nomination_counts() as nomination_counts:
                    nomination_counts[title] = nomination_counts.get(title, 0) + 1
                    if nomination_counts[title] >= await self.config.guild(ctx.guild).nomination_threshold():
                        duration = self.config.guild(ctx.guild).duration()
                        await ctx.send(f"Voting for the title: {title} has started. Use the `vote` command to cast your vote.")
                        await asyncio.sleep(duration)  # wait for 5 minutes

                        # Tally the votes and assign the title
                        async with self.config.guild(ctx.guild).votes() as votes:
                            vote_counts = votes.get(title, {})
                            if vote_counts:
                                # Get the user with the most votes
                                winner_id, _ = max(vote_counts.items(), key=lambda x: x[1])

                                # Assign the title to the winner
                                async with self.config.guild(ctx.guild).titles() as titles:
                                    titles[title] = winner_id
                                
                                await ctx.send(f"The title: {title} has been awarded to <@{winner_id}>.")

    @notoriety.command()
    @checks.admin_or_permissions(manage_messages=True)
    async def nomination_threshold(self, ctx, threshold: int):
        """Set the number of nominations required to start voting"""
        if threshold > 0:
            await self.config.guild(ctx.guild).nomination_threshold.set(threshold)
            await ctx.send(f"Nominations threshold set to {threshold}.")
        else:
            await ctx.send("Please provide a positive number.")

    @notoriety.command()
    @checks.admin_or_permissions(manage_messages=True)
    async def vote_threshold(self, ctx, threshold: int):
        """Set the number of votes required to assign a title"""
        if threshold > 0:
            await self.config.guild(ctx.guild).vote_threshold.set(threshold)
            await ctx.send(f"Votes threshold set to {threshold}.")
        else:
            await ctx.send("Please provide a positive number.")

    @notoriety.command()
    async def vote(self, ctx, user: Union[discord.Member, discord.User], title: str):
        """Vote for a user to receive a title"""
        async with self.config.guild(ctx.guild).nominations() as nominations:
            if nominations.get(title) is None or user.id not in nominations[title]:
                await ctx.send(f"{user.mention} has not been nominated for the title: {title}")
                return

        async with self.config.guild(ctx.guild).votes() as votes:
            if votes.get(title) is None:
                votes[title] = {}

            if votes[title].get(user.id) is None:
                votes[title][user.id] = 0

            votes[title][user.id] += 1
            await ctx.send(f"{ctx.author.mention} has voted for {user.mention} for the title: {title}")


    @notoriety.command()
    @checks.admin_or_permissions(manage_messages=True)
    async def title_duration(self, ctx, days: int):
        """Change the duration of title ownership"""
        if 7 <= days <= 30:
            await self.config.guild(ctx.guild).duration.set(days)
            await ctx.send(f"Title duration set to {days} days.")
        else:
            await ctx.send("Please provide a duration between 7 and 30 days.")

    @notoriety.command()
    async def view_titles(self, ctx):
        """View available titles and their current holders"""
        titles = await self.config.guild(ctx.guild).titles()
        embed = discord.Embed(title="User Titles", colour=discord.Colour.green())
        for title, user_id in titles.items():
            user = ctx.guild.get_member(user_id)
            embed.add_field(name=title, value=user.mention if user else "No holder")
        await ctx.send(embed=embed)