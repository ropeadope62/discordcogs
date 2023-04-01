import discord
from redbot.core import Config, commands, checks
from collections import defaultdict
import asyncio

class Notoriety(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=402944901290)
        self.nominations = defaultdict(lambda: defaultdict(int))
        self.votes = defaultdict(lambda: defaultdict(int))

        default_guild = {
            "titles": ['king','serf','noble'], "req_nominations": 2
        }
        self.config.register_guild(**default_guild)


    @commands.guild_only()
    @commands.group()
    async def titles(self, ctx):
        """Notoriety: Manage Notoriety Titles"""
        pass

    @titles.command(name="add")
    async def _add_title(self, ctx, *, title: str):
        """Notoriety: Add a new title to the list """
        async with self.config.guild(ctx.guild).titles() as titles: 
            if title in titles:
                await ctx.send("This title already exists.")
            else: 
                titles.append(title)
                await ctx.send(f"Title {title} added successfully. ")

    @titles.command(name="remove")
    async def _remove_title(self, ctx, *, title: str):
        """Notoriety: Remove a title from the list"""
        async with self.config.guild(ctx.guild).titles() as titles: 
            if title not in titles: 
                await ctx.send("This title does not exist")
            else:
                titles.remove(title)
                await ctx.send(f"Title '{title} removed successfully ")

    @commands.guild_only()
    @commands.group()
    async def nominations(self, ctx):
        """Notoriety: Manage Nomination Rules"""
        pass

    @nominations.command(name="required")
    async def _nominations_required(self, ctx, req_nominations: int):
        """Notoriety: Set the number of required nominations to call a vote"""
        async with self.config.guild(ctx.guild).req_nominations() as req_nominations:
            if req_nominations < 5 >= 10:
                await ctx.send("The number of required nominations can be set from 5 to 10")
            else: 
                req_nominations = req_nominations 

    @commands.guild_only()
    @commands.command()
    async def nominate(self, ctx, user: discord.Member, title: str):
        """Nominate a user for a Notoriety tile."""
        
        req_nominations = await self.config.guild(ctx.guild).req_nominations()

        titles = await self.config.guild(ctx.guild).titles()
        if title not in titles:
            await ctx.send("This title does not exist.")
            return
        
        if self.nominations[ctx.guild.id][user.id] == req_nominations:
            await ctx.send(f"{user.mention} has already been nominated for this title.")
            return

        self.nominations[ctx.guild.id][user.id] += 1

        if self.nominations[ctx.guild.id][user.id] == req_nominations:
            await ctx.send(f"{user.mention} has been nominated 3 times for the title '{title}'. Voting has started.")
            await self.initiate_voting(ctx, user, title)
        else:
            remaining = 3 - self.nominations[ctx.guild.id][user.id]
            await ctx.send(f"{user.mention} has been nominated for the title '{title}'. {remaining} more nominations needed.")

    async def initiate_voting(self, ctx, user, title):
        self.votes[ctx.guild.id][user.id] = 0

        def check(reaction, voter):
            return (
                str(reaction.emoji) == '👍'
                and voter != self.bot.user
                and reaction.message.id == vote_message.id
            )

        vote_message = await ctx.send(f"Vote to award {user.mention} the title '{title}'. React with 👍 to vote 'yes'.")
        
        await vote_message.add_reaction('👍')

        while self.votes[ctx.guild.id][user.id] < 10:
            try:
                reaction, voter = await self.bot.wait_for("reaction_add", check=check, timeout=300)
                self.votes[ctx.guild.id][user.id] += 1
                remaining_votes = 10 - self.votes[ctx.guild.id][user.id]
                await ctx.send(f"{voter.mention} voted 'yes'. {remaining_votes} more 'yes' votes needed.")
            except asyncio.TimeoutError:
                await ctx.send(f"Voting for {user.mention} to receive the title '{title}' has ended due to inactivity.")
                return

        await ctx.send(f"{user.mention} has received 10 'yes' votes and has been awarded the title '{title}'.")

        # Reset votes and nominations for this user and title
        self.votes[ctx.guild.id][user.id] = 0
        self.nominations[ctx.guild.id][user.id] = 0