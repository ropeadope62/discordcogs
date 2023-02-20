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

class RussianRoulette(commands.Cog):
    def __init__(self, bot):
        self.config = Config.get_conf(self, 45465465488435321554, force_registration=True)
        self.players = FancyDictList()
        self.round_started = FancyDict()
        self.winners = FancyDictList()
        self.dead = FancyDictList()
        self.current_player = FancyDictList()
        self.player_numbers = {}

        guild_defaults = {
            "Wait": 20,
            "Buyin": 1000,
            "Prize": 0,
            "playermaxcount": 6,
        }
        
        member_defaults = {"Wins": 0, "Losses": 0}

        self.config.register_guild(**guild_defaults)
        self.config.register_member(**member_defaults)
    
        
    async def red_delete_data_for_user(self, *, requester: Literal["discord", "owner", "user", "user_strict"], user_id: int):
        all_members = await self.config.all_members()
        async for guild_id, guild_data in AsyncIter(all_members.items(), steps=100):
            if user_id in guild_data:
                await self.config.member_from_ids(guild_id, user_id).clear()

    @commands.group()
    @commands.guild_only()
    async def russianroulette(self, ctx):
        pass
    @russianroulette.command()
    async def start(self, ctx):
        """Begins a new race.

        You cannot start a new race until the active on has ended.

        If you are the only player in the race, you will race against
        your bot.

        The user who started the race is automatically entered into the race.
        """
        if self.round_started[ctx.guild.id]:
            return await ctx.send(f"A game is already in progress,  Type `{ctx.prefix}russianroullete join` to join!")
        self.round_started[ctx.guild.id] = True
        self.players[ctx.guild.id].append(ctx.author)
        wait = await self.config.guild(ctx.guild).Wait()
        await ctx.send(
            f"🚩 A game of Russian Roulette has begun! Type {ctx.prefix}russianroulette join "
            f"to join the game! 🚩\nThe round will begin in "
            f"{wait} seconds!\n\n**{ctx.author.mention}** entered the game!"
        )

        await asyncio.sleep(wait)
        self.started[ctx.guild.id] = True
        await ctx.send("🏁 A game is now in progress. 🏁")
        await self.run_game(ctx)

        settings = await self.config.guild(ctx.guild).all()
        currency = await bank.get_currency_name(ctx.guild)
        color = await ctx.embed_colour()
        msg, embed = await self._build_end_screen(ctx, settings, currency, color)
        await ctx.send(content=msg, embed=embed)
        await self._race_teardown(ctx, settings)

        @russianroulette.command()
        async def stats(self, ctx, user: discord.Member = None):
            """Display your russian roulette stats."""
            if not user:
                user = ctx.author
            color = await ctx.embed_colour()
            user_data = await self.config.member(user).all()
            player_total = sum(user_data["Wins"].values()) + user_data["Losses"]
            embed = discord.Embed(color=color, description="Race Stats")
            embed.set_author(name=f"{user}", icon_url=user.avatar_url)
            embed.add_field(
                name="Wins",
                value=(
                    f"Wins: {user_data['Wins']}"
                ),
            )
            embed.add_field(name="Losses", value=f'{user_data["Losses"]}')
            await ctx.send(embed=embed)
            
        @russianroulette.command()
        async def join(self, ctx):
            """Join a game of Russian Roulette

            """
            if self.started[ctx.guild.id]:
                return await ctx.send(
                    "A game has already started, wait for the previous round to finish"
                )
            elif not self.round_started.get(ctx.guild.id):
                return await ctx.send("A game must be started before you can enter.")
            elif ctx.author in self.players[ctx.guild.id]:
                return await ctx.send("You have already entered the game.")
            elif len(self.players[ctx.guild.id]) >= 6:
                return await ctx.send("The maximum number of players has been reached.")
            else:
                self.players[ctx.guild.id].append(ctx.author)
                await ctx.send(f"{ctx.author.mention} has joined the game.")

        @russianroulette.command(hidden=True)
        @checks.admin_or_permissions(administrator=True)
        async def clear(self, ctx):                                                     
            """ONLY USE THIS COMMAND FOR DEBUGPURPOSES

            You shouldn't use this command unless the round is stuck
            or you are debugging."""
            self.clear_local(ctx)
            await ctx.send("Round cleared.")

        @russianroulette.command()
        @checks.is_owner()
        async def wipe(self, ctx):
            """This command will wipe ALL race data.

            You are given a confirmation dialog when using this command.
            If you decide to wipe your data, all stats and settings will be deleted.
            """
            await ctx.send(
                f"You are about to clear all russianroulette data including stats and settings. "
                f"If you are sure you wish to proceed, type `{ctx.prefix}yes`."
            )
            choices = (f"{ctx.prefix}yes", f"{ctx.prefix}no")
            check = lambda m: (m.author == ctx.author and m.channel == ctx.channel and m.content in choices)
            try:
                choice = await ctx.bot.wait_for("message", timeout=20.0, check=check)
            except asyncio.TimeoutError:
                return await ctx.send("No response. russian roulette wipe cancelled.")

            if choice.content.lower() == f"{ctx.prefix}yes":
                await self.config.guild(ctx.guild).clear()
                await self.config.clear_all_members(ctx.guild)
                return await ctx.send("russian roulette data has been wiped.")
            else:
                return await ctx.send("russian roulette wipe cancelled.")
            
        @russianroulette.command()
        async def version(self, ctx):
            """Displays the version of russian roulette."""
            await ctx.send(f"You are running russian roulette version {__version__}.")

        @setrussianroulette.command()
        async def wait(self, ctx, wait: int):
            """Changes the wait time before a game starts.

            This only affects the period where game is still waiting
            for more participants to join the game."""
            if wait < 0:
                return await ctx.send("Really? You're an idiot.")
            await self.config.guild(ctx.guild).Wait.set(wait)
            await ctx.send(f"Wait time before a game begins is now {wait} seconds.")

        @checks.is_owner()
        @setrussianroulette.group(name="buyin")
        async def buyin(self, ctx, amount: int ):
            """Buyin."""
            await self.config.guild(ctx.guild).Buyin.set(amount)
            await ctx.send(f"Buy in amount set to {amount}.")



    