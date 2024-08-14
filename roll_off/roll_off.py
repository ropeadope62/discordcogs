from redbot.core import commands, bank
import discord
import asyncio
import random

active_games = {}

class RollOff(commands.Cog):
    """Dice roll off for tokens."""

    def __init__(self, bot):
        self.bot = bot
        self.dice_emoji = {
            1: "<:dice_1:755891608859443290>", 2: "<:dice_2:1234915007800672337>",
            3: "<:dice_3:1234915030022225930>", 4: "<:dice_4:1234915065971609721>",
            5: "<:dice_5:1234915088448622802>", 6: "<:dice_6:1234915124582678610>"
        }


    @commands.command(aliases=['rolloff'])
    async def roll_off(self, ctx, opponent: discord.Member, bet: int):
        """Initiates a dice roll-off with an opponent for a specified bet."""
        if ctx.channel.id in active_games:
            await ctx.send("There is already a Roll Off in progress in this channel.")
            return
        
        if not await bank.can_spend(ctx.author, bet):
            await ctx.send(f"You do not have enough credits to make this bet. You need {bet - await bank.get_balance(ctx.author)} more.")
            return

        if opponent == ctx.author:
            await ctx.send("You can't roll off against yourself!")
            return

        if not await bank.can_spend(opponent, bet):
            await ctx.send(f"{opponent.mention} does not have enough credits to make this bet.")
            return

        active_games[ctx.channel.id] = True
        game_message = await ctx.send(f"{opponent.mention}, do you accept the challenge? Type 'yes' to accept or 'no' to decline.")

        def check(m):
            return m.author == opponent and m.content.lower() in ["yes", "no"]

        try:
            response = await self.bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            await game_message.edit(content="You took too long to respond, the challenge was cancelled.")
            active_games.pop(ctx.channel.id, None)
            return

        if response.content.lower() == "yes":
            await self.perform_roll_off(ctx, ctx.author, opponent, bet, game_message)
        else:
            await game_message.edit(content=f"{opponent.mention} declined the challenge. No game will be played.")
            active_games.pop(ctx.channel.id, None)


    async def perform_roll_off(self, ctx, challenger, opponent, bet, game_message=None):
        """Performs the actual roll-off and handles result, updating a single message to reduce spam."""
        currency_name = await bank.get_currency_name(ctx.guild)
        
        if not game_message:
            game_message = await ctx.send("The roll off has begun!")
        await asyncio.sleep(1) 
        # Challenger rolls
        challenger_roll = random.randint(1, 6)
         # Simulate rolling time
        await game_message.edit(content=f'{challenger.mention} rolls the dice... {self.dice_emoji[challenger_roll]} {challenger.mention} rolled a {challenger_roll}!')
        # Opponent rolls
        await asyncio.sleep(2)
        opponent_roll = random.randint(1, 6)
        await game_message.edit(content=f'{game_message.content}\nCan {opponent.mention} beat that? {opponent.mention} rolls the dice...')
        await asyncio.sleep(2)
        await game_message.edit(content=f'{game_message.content} {self.dice_emoji[opponent_roll]} {opponent.mention} rolled a {opponent_roll}!')
        await asyncio.sleep(2)
        # Determine the winner
        if challenger_roll > opponent_roll:
            winner, loser = challenger, opponent
            result_message = f"{challenger.mention} won the roll off and won {bet} {currency_name}!"
        elif challenger_roll < opponent_roll:
            winner, loser = opponent, challenger
            result_message = f"{opponent.mention} won the roll off and won {bet} {currency_name}!"
        else:
            await game_message.edit(content=f"{game_message.content}\nIt's a draw! No one won the bet.")
            active_games.pop(ctx.channel.id, None)
            return

        # Update the game result
        await bank.deposit_credits(winner, bet)
        await bank.withdraw_credits(loser, bet)
        await game_message.edit(content=f"{game_message.content}\n{result_message}")
        await asyncio.sleep(5)

        # Offer double or nothing if there was a winner
        if challenger_roll != opponent_roll:
            await self.offer_double_or_nothing(ctx, winner, loser, bet, game_message)



    async def offer_double_or_nothing(self, ctx, winner, loser, bet, game_message):
        """Offers a double or nothing challenge to the loser, updates the same game message."""
        currency_name = await bank.get_currency_name(ctx.guild)
        response_message = f"\n{loser.mention}, do you want to challenge {winner.mention} for double or nothing? The new bet is {bet * 2} {currency_name}, Type 'yes' to accept."
        await game_message.edit(content=f"{game_message.content}{response_message}")
        
        try: 
            response = await self.bot.wait_for('message', check=lambda m: m.author == loser and m.content.lower() in ["yes", "no"])
        
        except asyncio.TimeoutError:
            await game_message.edit(content="You took too long to respond, the challenge was cancelled.")
            active_games.pop(ctx.channel.id, None)
            return
        

        if response.content.lower() == "yes":
            await game_message.edit(content=f"{game_message.content}\n{winner.mention}, {loser.mention} has challenged you for double or nothing. There are {bet * 2} {currency_name} on the line! Do you accept? Type 'yes' to proceed.")
            response_winner = await self.bot.wait_for('message', check=lambda m: m.author == winner and m.content.lower() in ["yes", "no"])

            if response_winner.content.lower() == "yes":
                await game_message.edit(content=f"{game_message.content}\n**Let's Roll off for double or nothing!**")
                await asyncio.sleep(2)
                await self.perform_roll_off(ctx, loser, winner, 2 * bet)
            else:
                await game_message.edit(content=f"{game_message.content}\n{winner.mention} declined the double or nothing challenge.")
                active_games.pop(ctx.channel.id, None)
        else:
            await game_message.edit(content=f"{game_message.content}\n{loser.mention} declined the double or nothing challenge.")
            active_games.pop(ctx.channel.id, None)
        

