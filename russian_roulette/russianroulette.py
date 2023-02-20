import asyncio
import random
import discord
from discord.ext import commands
from redbot.core import Config, bank, commands, checks
from redbot.core.utils import AsyncIter
from redbot.core.errors import BalanceTooHigh

class RussianRoulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = []
        self.game_started = False
        self.current_player = None
        self.player_numbers = {}


    @commands.group()
    @commands.guild_only()
    async def russianroulette(self, ctx):
        pass
    @russianroulette.command()
    async def start(self, ctx):

        if self.game_started:
            await ctx.send("A game is already in progress.")
            return
        counter = 0
        await ctx.send("Type 'join' to join the game. You have 30 seconds.")
        def check(message):
            return message.author != ctx.bot.user and message.content.lower() == "join"       
        while counter < 6:
            try:
                messages = await self.bot.wait_for("message", check=check, timeout=30)
                counter += 1
            except asyncio.TimeoutError:
                pass
        
        if not self.players:
            await ctx.send("Not enough players. Game cancelled.")
            return

        self.game_started = True
        await ctx.send("Game starting with {} players!".format(len(self.players)))
        self.player_numbers = {p: n for n, p in enumerate(random.sample(self.players, 6), 1)}

        self.current_player = random.choice(self.players)
        await ctx.send("The game will start with {}.".format(self.current_player.mention))
        

    @russianroulette.command()
    async def shoot(self, ctx):
        if not self.game_started:
            await ctx.send("No game in progress.")
            return

        if self.current_player != ctx.author:
            await ctx.send("It's not your turn!")
            return

        number = self.player_numbers[ctx.author]
        await ctx.send("{0.mention} ***CLICK!***".format(ctx.author, number))

        if number == 3:
            await ctx.send("{0.mention} wins!".format(ctx.author))
            self.game_started = False
            return
        
        self.current_player = self.get_next_player(ctx.author)
        await ctx.send("Next up: {0.mention}.".format(self.current_player))
        
    def get_next_player(self, current_player):
        index = self.players.index(current_player)
        return self.players[(index + 1) % len(self.players)]
        
    @russianroulette.command()
    async def cancel(self, ctx):
        if not self.game_started:
            await ctx.send("No game in progress.")
            return
        
        self.game_started = False
        await ctx.send("Game cancelled.")
    
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        if message.content.lower() == "join" and message.channel.type == discord.TextChannel:
            if message.author not in self.players:
                self.players.append(message.author)
                await message.add_reaction("✅")


