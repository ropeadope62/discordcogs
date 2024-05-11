from redbot.core import commands, bank, Config
import discord
import random
import logging
from redbot.core import bank


logger = logging.getLogger("scrap.powerballs")

class Powerballs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=12312324545665484789021415623423, force_registration=True)
        default_guild = {
            "tickets": {}, 
            "jackpot": 0,
            "winners": {},
            "total_tickets_bought": 0,
            "ticket_price": 500
        }
        self.config.register_guild(**default_guild)
    
    @commands.group()
    async def powerballs(self, ctx):
        """The Sanctuary Powerballs Lottery! If you want more luck, take more chances!\n *Subcommands:*\n `buyticket` - Buy a ticket for the lottery.\n 'showtickets' - Show how many tickets you own for the next draw."""
        pass

    @powerballs.command(aliases=["buyticket"])
    async def buytickets(self, ctx, number_of_tickets: int):
        """Buy Powerballs lottery tickets."""
        ticket_price = await self.config.guild(ctx.guild).ticket_price()
        cost = ticket_price * number_of_tickets
        user_balance = await bank.get_balance(ctx.author)
        currency_name = await bank.get_currency_name(ctx.guild)
        if cost > user_balance:
            await ctx.send(f"You don't have enough {currency_name} to buy these tickets.")
            return  # Ensure no further processing if the user cannot afford the tickets

        await bank.withdraw_credits(ctx.author, cost)      
        user_id_str = str(ctx.author.id)  # Convert to string for consistency
        tickets = await self.config.guild(ctx.guild).tickets()

        # Initialize an empty list for the user's tickets if not already present
        if user_id_str not in tickets:
            tickets[user_id_str] = []
            logger.debug(f"User {user_id_str} added to tickets dict")

        # Append the ticket numbers to the user's list of tickets
        for _ in range(number_of_tickets):
            ticket_number = random.randint(1000, 9999)
            tickets[user_id_str].append(ticket_number)
            logger.debug(f"User {user_id_str} bought ticket {ticket_number}")

        await self.config.guild(ctx.guild).tickets.set(tickets)  # Set the updated tickets dictionary
        logger.debug(f"Tickets set to {tickets}") 
        await ctx.send(f"You've successfully bought {number_of_tickets} tickets for {cost} {currency_name}!")


    @powerballs.command()
    async def mytickets(self, ctx):
        """ Show how many Powerballs tickets you have. """
        user_id = str(ctx.author.id)
        guild_id = ctx.guild.id
        
        # Attempt to fetch the ticket numbers for the user.
        try:
            tickets = await self.config.guild_from_id(guild_id).tickets.get_raw(default={})
            user_tickets = tickets.get(user_id, [])
            if user_tickets:
                await ctx.send(f"You have {len(user_tickets)} Powerballs tickets.")
            else:
                await ctx.send("You have no tickets.")
        except KeyError:
            # Handle cases where the specific user's ticket entry does not exist.
            await ctx.send("You have no tickets registered.")
        
    @powerballs.command()
    async def totaltickets(self, ctx):
        guild_id = ctx.guild.id
        
        # Fetch the tickets dictionary from the guild configuration
        try:
            tickets = await self.config.guild_from_id(guild_id).tickets()
            if tickets:
                total_tickets = sum(len(user_tickets) for user_tickets in tickets.values())
                if total_tickets > 0:
                    await ctx.send(f"There are a total of {total_tickets} tickets.")
                else:
                    await ctx.send("There are currently no tickets.")
            else:
                await ctx.send("There are currently no tickets.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @powerballs.command()
    async def checktickets(self, ctx):
        user_id = str(ctx.author.id)
        guild_id = ctx.guild.id
        
        # Fetch the user's ticket numbers.
        try:
            tickets = await self.config.guild_from_id(guild_id).tickets()
            user_tickets = tickets.get(user_id, [])
            if user_tickets:
                ticket_list = ', '.join(map(str, user_tickets))
                await ctx.send(f"Your tickets: {ticket_list}")
            else:
                await ctx.send("You currently have no tickets.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
        
    @powerballs.command()
    async def viewjackpot(self, ctx):
        """View the current Powerballs jackpot amount."""
        guild_id = ctx.guild.id
        # Retrieve the entire tickets data from the guild configuration
        try:
            tickets = await self.config.guild_from_id(guild_id).tickets()
            if not tickets:
                await ctx.send("There are currently no tickets sold.")
                return

            ticket_price = await self.config.guild(ctx.guild).ticket_price()

            # Calculate the total number of tickets sold
            total_tickets = sum(len(user_tickets) for user_tickets in tickets.values())
            jackpot = total_tickets * ticket_price

            currency_name = await bank.get_currency_name(ctx.guild)
            await ctx.send(f"The current Powerballs jackpot amount is {jackpot} {currency_name}.")
        except Exception as e:
            await ctx.send(f"An error occurred while retrieving jackpot information: {str(e)}")

    

    @powerballs.command()
    async def pastwinners(self, ctx):
        """View past winners of the Powerballslottery."""
        guild_id = ctx.guild.id 
        winners = await self.config.guild(guild_id).winners()
        if not winners:
            await ctx.send("No past winners.")
            return
        currency_name = await bank.get_currency_name(guild_id)
        message = "Past Winners:\n"
        for user_id, amount in winners.items():
            user = ctx.guild.get_member(int(user_id))
            if user:
                message += f"{user.display_name} won {amount} {currency_name}.\n"
            else:
                message += f"User ID {user_id} won {amount} {currency_name}.\n"
        
        await ctx.send(message)
    
    @powerballs.command()
    @commands.is_owner()
    async def drawwinner(self, ctx):
        """Draw the winner of the lottery."""
        tickets = await self.config.guild(ctx.guild).tickets()
        if not tickets:
            await ctx.send("No tickets have been sold.")
            return

        # Flatten the list of all tickets
        all_tickets = [ticket for user_tickets in tickets.values() for ticket in user_tickets]
        if not all_tickets:
            await ctx.send("No tickets have been sold.")
            return

        winning_ticket = random.choice(all_tickets)

        # Find the winner
        winner_id = None
        for user_id, user_tickets in tickets.items():
            if winning_ticket in user_tickets:
                winner_id = int(user_id)  # Ensure winner_id is an integer
                break

        if winner_id:
            winner = await ctx.guild.fetch_member(winner_id)  # Use fetch_member to get the member object
            jackpot = await self.config.guild(ctx.guild).jackpot()
            if winner:
                await bank.deposit_credits(winner, jackpot)
                await ctx.send(f"Congratulations {winner.mention}, you won the jackpot of {jackpot} credits!")
                # Record the winner
                async with self.config.guild(ctx.guild).winners() as winners:
                    winners[str(winner_id)] = jackpot
                # Reset for the next round
                await self.config.guild(ctx.guild).tickets.set({})
                await self.config.guild(ctx.guild).jackpot.set(0)
            else:
                await ctx.send("Winner not found in the guild.")
        else:
            await ctx.send("An error occurred while drawing the winner.")