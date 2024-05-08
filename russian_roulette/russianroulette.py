# Standard Library
import asyncio
import itertools
import random
import discord
import contextlib

# Russian Roulette
from .kill import outputs

# Red
from redbot.core import Config, bank, checks, commands
from redbot.core.errors import BalanceTooHigh


__version__ = "3.1.07"
__authors__ = "Redjumpman", "Slurms Mackenzie/ropeadope62"

channel_game_states = {}


class RussianRoulette(commands.Cog):
    defaults = {
        "Cost": 100,
        "Chamber_Size": 6,
        "Wait_Time": 30,
        "Session": {"Pot": 0, "Players": [], "Active": False, "Betting": False, "Bets": {}}
    }

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 5074395012323404, force_registration=True)
        self.config.register_guild(**self.defaults)

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

    @commands.group(autohelp=True)
    @commands.guild_only()
    async def rr(self, ctx):
        """Russian Roulette by RedJumpman
        Betting functions by Slurms Mackenzie
        Party on dudes!"""
        
        if ctx.invoked_subcommand is None:
            # Handle the case where no subcommand is provided
            await ctx.send("Please specify a subcommand. Use `help rr` for more information.")  
        
            
    @commands.guild_only()
    @commands.cooldown(1, 300, commands.BucketType.user)
    @rr.command()
    async def play(self, ctx):
        """Start or join a game of russian roulette.

        The game will not start if no players have joined. That's just
        suicide.

        The maximum number of players in a circle is determined by the
        size of the chamber. For example, a chamber size of 6 means the
        maximum number of players will be 6.
        """
        print('Play game function started')
        settings = await self.config.guild(ctx.guild).all()
        if await self.game_checks(ctx, settings):
            print('adding players to the game')
            await self.add_player(ctx, settings["Cost"])
            print('Player was added')
            print('adding players to the game')
            
    @rr.command()
    async def bet(self, ctx, amount: int, channel_id):
        """Place a bet on the Russian Roulette game."""
        settings = await self.config.guild(ctx.guild).all()
        if not settings["Session"]["Betting"]:
            print('Betting was attempted but betting phase closed')
            return await ctx.send("Betting is currently closed.")
        player_ids = [player["id"] for player in settings["Session"]["Players"]]
        if ctx.author.id not in player_ids:
            print('Player is not in session players')
            return await ctx.send("You must be in the game to place a bet.")
        try:
            await bank.withdraw_credits(ctx.author, amount)
            print('Player bet was accepted')
        except ValueError:
            await ctx.send("You don't have enough credits to place this bet.")
            return

        # Update the player's bet
        print('Updating player bet')
        async with self.config.guild(ctx.guild).Session.Bets() as bets:
            player_id = str(ctx.author.id)
            bets[player_id] = bets.get(player_id, 0) + amount

        await ctx.send(f"{ctx.author.mention} has placed a bet of {amount} credits.")

    @commands.guild_only()
    @checks.admin_or_permissions(administrator=True)
    @commands.command(hidden=True)
    async def rrreset(self, ctx):
        """ONLY USE THIS FOR DEBUGGING PURPOSES"""
        await self.config.guild(ctx.guild).Session.clear()
        await ctx.send("The Russian Roulette session on this server has been cleared.")

    @commands.command()
    async def rrversion(self, ctx):
        """Shows the cog version for RussianRoulette."""
        await ctx.send("You are using russian roulette version {}".format(__version__))

    @commands.group(autohelp=True)
    @commands.guild_only()
    @checks.admin_or_permissions(administrator=True)
    async def setrr(self, ctx):
        """Russian Roulette Settings group."""
        pass

    @setrr.command()
    async def chamber(self, ctx, size: int):
        """Sets the chamber size of the gun used. MAX: 12."""
        if not 1 < size <= 12:
            return await ctx.send("Invalid chamber size. Must be in the range of 2 - 12.")
        await self.config.guild(ctx.guild).Chamber_Size.set(size)
        await ctx.send("Chamber size set to {}.".format(size))

    @setrr.command()
    async def cost(self, ctx, amount: int):
        """Sets the required cost to play."""
        if amount < 0:
            return await ctx.send("You are an idiot.")
        await self.config.guild(ctx.guild).Cost.set(amount)
        currency = await bank.get_currency_name(ctx.guild)
        await ctx.send("Required cost to play set to {} {}.".format(amount, currency))

    @setrr.command()
    async def wait(self, ctx, seconds: int):
        """Set the wait time (seconds) before starting the game."""
        if seconds <= 0:
            return await ctx.send("You are an idiot.")
        await self.config.guild(ctx.guild).Wait_Time.set(seconds)
        await ctx.send("The time before a roulette game starts is now {} seconds.".format(seconds))

    async def game_checks(self, ctx, settings):
        player_ids = [player["id"] for player in settings["Session"]["Players"]]
        if ctx.author.id in player_ids:
            await ctx.send("You are already in the roulette circle.")
            return False

        if len(settings["Session"]["Players"]) == settings["Chamber_Size"]:
            print('Roulette circle is full')
            await ctx.send("The roulette circle is full. Wait for this game to finish to join.")
            return False

        try:
            print('Checking if player has enough credits')
            await bank.withdraw_credits(ctx.author, settings["Cost"])
            
        except ValueError:
            currency = await bank.get_currency_name(ctx.guild)
            await ctx.send("Insufficient funds! This game requires {} {}.".format(settings["Cost"], currency))
            return False
        else:
            print('Passed checks, adding player to the game')
            return True

    async def add_player(self, ctx, cost):
        print('Getting current pot')
        current_pot = await self.config.guild(ctx.guild).Session.Pot()
        print('Setting new pot value')
        await self.config.guild(ctx.guild).Session.Pot.set(value=(current_pot + cost))
        
        async with self.config.guild(ctx.guild).Session() as session:
            if len(session["Players"]) == 0:
                session["Initiator"] = ctx.author.id

        async with self.config.guild(ctx.guild).Session.Players() as players:
            players.append({"id": ctx.author.id, "bet": 0})
            print('Adding player to session players')
            print('Getting number of players')
            num_players = len(players)

        if num_players == 1:
            print('Starting game start countdown and betting')
            wait = await self.config.guild(ctx.guild).Wait_Time()
            print('Setting betting to true')
            await self.config.guild(ctx.guild).Session.Betting.set(True)
            await ctx.send(
                "{0.author.mention} is gathering players for a game of russian "
                "roulette!\nType `{0.prefix}rr play` to enter.\n"
                "Remember to bet before the game starts with {0.prefix}rr bet! Winner takes all!"
                "The round will start in {1} seconds.".format(ctx, wait)
            )
            print('Waiting for betting phase to end')
            await asyncio.sleep(wait)
            print('Betting phase ended')
            await self.config.guild(ctx.guild).Session.Betting.set(False)
            print('Starting game logic')
            await self.start_game(ctx)
            
        else:
            await ctx.send("{} was added to the roulette circle.".format(ctx.author.mention))

    async def start_game(self, ctx):
        await self.config.guild(ctx.guild).Session.Active.set(True)
        session_data = await self.config.guild(ctx.guild).Session.all()
        total_pot = session_data["Pot"]

        # Calculate the total pot including bets
        total_winnings = total_pot + sum(session_data["Bets"].values())
        await ctx.send(f'The game has started! Winner takes all with {total_winnings} credits on the line. Good luck!')
        players = [ctx.guild.get_member(player["id"]) for player in session_data["Players"]]
        filtered_players = [player for player in players if isinstance(player, discord.Member)]
        if len(filtered_players) < 2:
            try:
                await bank.deposit_credits(ctx.author, session_data["Pot"])
            except BalanceTooHigh as e:
                await bank.set_balance(ctx.author, e.max_balance)
            await self.reset_game(ctx)
            return await ctx.send("You can't play by youself. That's just suicide.")
        chamber = await self.config.guild(ctx.guild).Chamber_Size()

        counter = 1
        while len(filtered_players) > 1:
            await ctx.send(
                "**Round {}**\n*{} spins the cylinder of the gun "
                "and with a flick of the wrist it locks into "
                "place.*".format(counter, ctx.bot.user.name)
            )
            await asyncio.sleep(3)
            await self.start_round(ctx, chamber, filtered_players)
            counter += 1
        await self.game_teardown(ctx, filtered_players)

    async def start_round(self, ctx, chamber, players):
        position = random.randint(1, chamber)
        while True:
            for turn, player in enumerate(itertools.cycle(players), 1):
                await ctx.send(
                    "{} presses the revolver to their head and slowly squeezes the trigger...".format(player.name)
                )
                await asyncio.sleep(5)
                if turn == position:
                    players.remove(player)
                    msg = "**BANG!** {0} is now dead.\n"
                    msg += random.choice(outputs)
                    await ctx.send(msg.format(player.mention, random.choice(players).name, ctx.guild.owner))
                    await asyncio.sleep(3)
                    break
                else:
                    await ctx.send("**CLICK!** {} passes the gun along.".format(player.name))
                    await asyncio.sleep(3)
            break

    async def game_teardown(self, ctx, players):
        print('Started game teardown')
        winner = players[0]
        currency = await bank.get_currency_name(ctx.guild)

        session_data = await self.config.guild(ctx.guild).Session.all()
        total_pot = session_data["Pot"]

        # Calculate the total pot including bets
        total_winnings = total_pot + sum(session_data["Bets"].values())

        try:
            print('Awarding the winner')
            await bank.deposit_credits(winner, total_winnings)
        except BalanceTooHigh as e:
            await bank.set_balance(winner, e.max_balance)
        
        await self.reset_game(ctx)

        try:        
            await bank.deposit_credits(winner, total_winnings)
            await ctx.send(
            f"Congratulations {winner.mention}! You are the last person standing and have "
            f"won a total of {total_winnings} {currency}."
        )
        except BalanceTooHigh as e:
            await bank.set_balance(winner, e.max_balance)

        await self.reset_game(ctx)

    async def reset_game(self, ctx):
        async with self.config.guild(ctx.guild).Session() as session:
            session["Players"] = []
            session['Pot'] = 0
            session["Bets"] = {}
