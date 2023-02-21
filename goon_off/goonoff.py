import asyncio
import random
import discord
from discord.ext import commands
from redbot.core import Config, bank, commands, checks
from redbot.core.utils import AsyncIter
from redbot.core.errors import BalanceTooHigh
from typing import Literal

class FancyDict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


class FancyDictList(dict):
    def __missing__(self, key):
        value = self[key] = []
        return value

class GoonOff(commands.Cog):
    def __init__(self, bot):
        self.config = Config.get_conf(self, 45465465488435321554234, force_registration=True)
        self.players = FancyDictList()
        self.active = FancyDict()
        self.bot = bot

        guild_defaults = {
            "Wait": 20,
            "Chambers": 6,
        }
        
        member_defaults = {"Wins": 0, "Losses": 0, "Total_Winnings": 0 }

        self.config.register_guild(**guild_defaults)
        self.config.register_member(**member_defaults)
    
        
    async def red_delete_data_for_user(self, *, requester: Literal["discord", "owner", "user", "user_strict"], user_id: int):
        all_members = await self.config.all_members()
        async for guild_id, guild_data in AsyncIter(all_members.items(), steps=100):
            if user_id in guild_data:
                await self.config.member_from_ids(guild_id, user_id).clear()

    @commands.group()
    @commands.guild_only()
    async def goonoff(self, ctx):
        pass
    @goonoff.command()
    async def challenge(self, ctx, opponent: discord.Member):
        """
        Start a game of Russian Roulette with the specified opponent.
        """
        wait = await self.config.guild(ctx.guild).Wait()
        chambers = await self.config.guild(ctx.guild).Chambers()
        if self.active[ctx.guild.id]:
            await ctx.send(f"A game of Russian Roulette is already in progress. Wait please.")
            return 
        if opponent == ctx.author:
            await ctx.send("You can't play Russian Roulette with yourself!")
            return
        else: 
            self.players[ctx.guild.id].append(ctx.author)
            await ctx.send(f"{opponent.mention}, do you accept this game of Russian Roulette? Type 'yes' or 'no'.")

        def check(msg):
            print(msg.content)
            return msg.author == opponent and msg.content.lower() in ['yes', 'no']

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=wait)
        except asyncio.TimeoutError:
            await ctx.send(f"{opponent.mention} didn't respond in time. Game cancelled.")
            return

        if msg.content.lower() == 'no':
            await ctx.send(f"{opponent.mention} declined the game. Game cancelled.")
            return

        # Both players accepted, set the session to active and add the opponent to players
    
        self.active[ctx.guild.id] = True
        self.players[ctx.guild.id].append(opponent)
        
        #This is for logging purposes
        print(self.players)
        print(self.players[ctx.guild.id][0])

        current_player = self.players[ctx.guild.id][random.randint(0, 1)]
        await ctx.send(f"{current_player} goes first.")

        # Set up the game with a bullet in one of the chambers
        maxchambers = await self.config.guild(ctx.guild).Chambers()
        chambers = [0] * maxchambers
        chambers[random.randint(0, maxchambers)] = 1

        # Play the game until someone loses
        while True:
        # Ask the player to pull the trigger
            await ctx.send(f"{current_player.mention}, it's your turn! Type 'pull' to pull the trigger.")

            def check(msg):
                print(msg.content)
                return msg.author == current_player and msg.content.lower() in ['pull']

            try:
                msg = await self.bot.wait_for('message', check=check, timeout=wait)
            except asyncio.TimeoutError:
                await ctx.send(f"{current_player.mention} chickened out. Game cancelled.")
                return
            
            if msg.content.lower() == 'pull':
                await ctx.send(f"{current_player.mention} pulls the trigger...")
            if chambers.pop(0) == 1:
                winner = self.players[ctx.guild.id][1] if current_player == self.players[ctx.guild.id][0] else self.players[ctx.guild.id][0]
                await ctx.send(f"{current_player.mention} pulled the trigger and the gun fired! {winner.mention} wins!")
                self.active[ctx.guild.id] = False
                break
            else:
                # Switch to the next player
                current_player = self.players[ctx.guild.id][1] if current_player == self.players[ctx.guild.id][0] else self.players[ctx.guild.id][0]