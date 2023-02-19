import asyncio
import random
import asyncio
import random
from typing import Literal

# Red
from redbot.core import Config, bank, commands, checks
from redbot.core.utils import AsyncIter
from redbot.core.errors import BalanceTooHigh

# Discord
import discord


class RussianRoulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = []
        self.game_started = False
        self.current_player = None
        self.player_numbers = {}
        self.config = Config.get_conf(self, 100737218252923221245194, force_registration=True)

   
    @commands.group()
    @commands.guild_only()    
    async def russianroulette(self, ctx):
        """Russian Roulette
              
        Feeling Lucky? 

        Begin a new round of Russian Roulette

        You cannot start a new round until the active on has ended.

        The user who started the round also takes part.
        """
        pass


    players = []

    # function to select a random player to start the game
    def select_start_player():
        return random.choice(players)

    # function to simulate pulling the trigger
    def pull_trigger():
        return random.randint(1,6) == 1

    # start a new game session if one isn't already in progress
    @russianroulette.command()
    async def start(self, players, ctx):
        global players
        players = []
        if len(players) == 0:
            await ctx.send("Starting a game of Russian Roulette! Type '!join' to join the game.")
            await asyncio.sleep(30)
            if len(players) < 2:
                await ctx.send("Game canceled due to lack of players.")
                return
            start_player = select_start_player()
            await ctx.send(f"{start_player.mention} will start the game. When it's your turn, type 'pull'.")
            index = players.index(start_player)
            while True:
                current_player = players[index]
                await ctx.send(f"{current_player.mention}, it's your turn. Type 'pull'.")
                try:
                    response = await bot.wait_for("ctx", check=lambda m: m.author == current_player and m.content.lower() == "pull", timeout=30)
                except asyncio.TimeoutError:
                    await ctx.send(f"{current_player.mention} has timed out and is out of the game!")
                    players.remove(current_player)
                    if len(players) == 1:
                        await ctx.send(f"Congratulations {players[0].mention}, you're the winner!")
                        players = []
                        break
                else:
                    if pull_trigger():
                        await ctx.send(f"{current_player.mention} is out! The game is over.")
                        players.remove(current_player)
                        if len(players) == 1:
                            await ctx.send(f"Congratulations {players[0].mention}, you're the winner!")
                            players = []
                            break
                    else:
                        await ctx.send(f"{current_player.mention} survived! Passing the gun to the next player.")
                index = (index + 1) % len(players)
        else:
            await ctx.send("A game is already in progress. Please wait for it to finish.")

    # function to handle player join requests
    @russianroulette.command()
    async def join(message):
        global players
        if len(players) < 6 and message.author not in players:
            players.append(message.author)
            await message.channel.send(f"{message.author.mention} has joined the game.")
        elif message.author in players:
            await message.channel.send(f"{message.author.mention} is already in the game.")
        else:
            await message.channel.send("Sorry, the game is already full.")


    @russianroulette.command()
    async def version(self, ctx):
        """Displays the version of Russian Roulette."""
        await ctx.send(f"Russian Roulette {__version__}. by Slurms Mackenzie (ropeadope62)")

