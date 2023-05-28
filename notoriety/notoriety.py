import discord
from redbot.core import commands
from datetime import datetime, timedelta
import asyncio
import json
import os

class Notoriety(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.votes = {}
        self.titles = self.load_titles()
        self.nominee = None
        self.nominator = None
        self.current_title = None
        self.cooldowns = {}

    def load_titles(self):
        if not os.path.isfile("notoriety_titles.json"):
            return {}
        with open("notoriety_titles.json", 'r') as f:
            titles = json.load(f)
            print(titles)
            return json.load(f)
    
    @commands.guild_only()
    @commands.group()
    async def notoriety(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid Notoriety command passed...')

    @notoriety.command()
    async def nominate(self, ctx, member: commands.MemberConverter, title: str):
        if self.nominee is not None:
            await ctx.send('A vote is currently in progress.')
            return

        if title not in self.titles:
            await ctx.send('Invalid title')
            return

        if member in self.cooldowns and title in self.cooldowns[member] and self.cooldowns[member][title] > datetime.now():
            await ctx.send('Title cooldown still active.')
            return

        await ctx.send(f'{ctx.author.mention} has nominated {member.mention} for title {title}. Please vote using ">notoriety vote yes" or ">notoriety vote no". You have 5 minutes.')

        self.nominee = member
        self.nominator = ctx.author
        self.current_title = title

        await asyncio.sleep(300)

        yes_votes = self.votes.get('yes', 0)

        if yes_votes >= self.titles[title]['required_votes']:
            await member.add_roles(discord.utils.get(ctx.guild.roles, name=title))
            if member not in self.cooldowns:
                self.cooldowns[member] = {}
            self.cooldowns[member][title] = datetime.now() + timedelta(days=30)
            await ctx.send(f'{member.mention} has been awarded the title {title}!')
        else:
            await ctx.send(f'{member.mention} has not been awarded the title {title}.')

        self.votes = {}
        self.nominee = None
        self.nominator = None
        self.current_title = None

    @notoriety.command()
    async def vote(self, ctx, vote: str):
        if self.nominee is None:
            await ctx.send('No vote is currently in progress.')
            return
        if vote not in ['yes', 'no']:
            await ctx.send('Invalid vote, please vote either "yes" or "no".')
            return
        if ctx.author in self.votes:
            await ctx.send('You have already voted.')
            return

        self.votes[ctx.author] = vote
        await ctx.send(f'{ctx.author.mention} voted {vote}!')