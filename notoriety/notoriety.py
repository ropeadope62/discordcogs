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
        self.cooldowns = {}

    def load_titles(self):
        with open("notoriety_titles.json", 'r') as f:
            data = json.load(f)
        return data

    async def add_title(self, user, title):
        self.titles[title]['title_holder'].append(user.id)
        with open("notoriety_titles.json", 'w') as f:
            json.dump(self.titles, f)

    
    @commands.guild_only()
    @commands.group()
    async def notoriety(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid Notoriety command passed...')

    @notoriety.command()
    async def nominate(self, ctx: commands.Context, user: discord.Member, title: str = None):
        if self.nominee is not None:
            print('A vote is currently in progress.')
            await ctx.send('A vote is currently in progress.')
            return
        
        if title not in self.titles:
            print(title)
            print(f'{self.titles}')
            await ctx.send('Invalid title')
            return

        if user in self.cooldowns and title in self.cooldowns[user] and self.cooldowns[user][title] > datetime.now():
            await ctx.send('Title cooldown still active.')
            return

        await ctx.send(f'{ctx.author.mention} has nominated {user.mention} for title {title}. Please vote using ">notoriety vote yes" or ">notoriety vote no". You have 5 minutes.')

        self.nominee = user
        self.nominator = ctx.author
        self.current_title = title

        await asyncio.sleep(20)

        yes_votes = self.votes.get('yes', 0)

        if yes_votes >= self.titles[title]['required_votes']:
           # add the users id to notoriety_titles.json
            await self.add_title(user, title)
        
            if user not in self.cooldowns:
                self.cooldowns[user] = {}
            self.cooldowns[user][title] = datetime.now() + timedelta(days=30)
            await ctx.send(f'{user.mention} has been awarded the title {title}!')
        else:
            await ctx.send(f'{user.mention} has not been awarded the title {title}.')


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