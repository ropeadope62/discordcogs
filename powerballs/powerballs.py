from redbot.core import commands, bank, Config
import discord
import random
import logging

from .powergeist import PowerGeist 

logger = logging.getLogger("scrap.powerballs")

class Powerballs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1231232454566548478902234552415623423, force_registration=True)
        default_guild = {
            "tickets": {}, 
            "jackpot": 0,
            "winners": {},
            "total_tickets_bought": 0,
            "ticket_price": 500,
            "geist_channel_id": None
        }
        self.config.register_guild(**default_guild)
        
        # Create an instance of the PowerGeist class
        self.powergeist = PowerGeist(self.bot)
        
        # Start the PowerGeist event loop with the run method. 
        self.bot.loop.create_task(self.powergeist.run())
    
    @commands.group()
    async def powerballs(self, ctx: commands.Context):
        """The Sanctuary Powerballs Lottery! If you want more luck, take more chances!
        \n *Subcommands:*\n `buyticket` - Buy a ticket for the lottery.\n `showtickets` - Show how many tickets you own for the next draw."""
        pass

    @powerballs.command(aliases=["buyticket"])
    async def buytickets(self, ctx: commands.Context, number_of_tickets: int):
        """Buy Powerballs lottery tickets."""
        ticket_price = await self.config.guild(ctx.guild).ticket_price()
        cost = ticket_price * number_of_tickets
        user_balance = await bank.get_balance(ctx.author)
        currency_name = await bank.get_currency_name(ctx.guild)
        if cost > user_balance:
            await ctx.send(f"You don't have enough {currency_name} to buy these tickets.")
            return

        await bank.withdraw_credits(ctx.author, cost)      
        user_id_str = str(ctx.author.id)
        tickets = await self.config.guild(ctx.guild).tickets()

        if user_id_str not in tickets:
            tickets[user_id_str] = []
            logger.debug(f"User {user_id_str} added to tickets dict")

        for _ in range(number_of_tickets):
            ticket_number = random.randint(1000, 9999999)
            tickets[user_id_str].append(ticket_number)
            logger.debug(f"User {user_id_str} bought ticket {ticket_number}")

        await self.config.guild(ctx.guild).tickets.set(tickets)
        logger.debug(f"Tickets set to {tickets}") 
        await ctx.send(f"You've successfully bought {number_of_tickets} tickets for {cost} {currency_name}!")

    @powerballs.command()
    async def mytickets(self, ctx: commands.Context):
        """Show how many Powerballs tickets you have."""
        user_id = str(ctx.author.id)
        tickets = await self.config.guild(ctx.guild).tickets()
        user_tickets = tickets.get(user_id, [])
        
        if user_tickets:
            await ctx.send(f"You have {len(user_tickets)} Powerballs tickets.")
        else:
            await ctx.send("You have no tickets.")

    @powerballs.command()
    async def totaltickets(self, ctx: commands.Context):
        """Show the total number of tickets sold."""
        tickets = await self.config.guild(ctx.guild).tickets()
        total_tickets = sum(len(user_tickets) for user_tickets in tickets.values())
        
        if total_tickets > 0:
            await ctx.send(f"There are a total of {total_tickets} tickets.")
        else:
            await ctx.send("There are currently no tickets.")

    @powerballs.command()
    async def checktickets(self, ctx: commands.Context):
        """Check your Powerballs tickets."""
        user_id = str(ctx.author.id)
        tickets = await self.config.guild(ctx.guild).tickets()
        user_tickets = tickets.get(user_id, [])
        
        if not user_tickets:
            await ctx.send("You currently have no tickets.")
            return

        paginator = commands.Paginator(prefix='', suffix='', max_size=2000)
        for ticket in user_tickets:
            paginator.add_line(str(ticket))

        for page in paginator.pages:
            embed = discord.Embed(title="Your Powerballs Tickets", description=page, color=discord.Color.purple())
            await ctx.send(embed=embed)
        
    @powerballs.command()
    async def viewjackpot(self, ctx: commands.Context):
        """View the current Powerballs jackpot amount."""
        tickets = await self.config.guild(ctx.guild).tickets()
        if not tickets:
            await ctx.send("There are currently no tickets sold.")
            return

        ticket_price = await self.config.guild(ctx.guild).ticket_price()
        total_tickets = sum(len(user_tickets) for user_tickets in tickets.values())
        jackpot = total_tickets * ticket_price
        currency_name = await bank.get_currency_name(ctx.guild)
        
        await ctx.send(f"The current Powerballs jackpot amount is {jackpot} {currency_name}.")
    
    @powerballs.command()
    async def pastwinners(self, ctx: commands.Context):
        """View past winners of the Powerballs lottery."""
        winners = await self.config.guild(ctx.guild).winners()
        if not winners:
            await ctx.send("No past winners.")
            return

        currency_name = await bank.get_currency_name(ctx.guild)
        embed = discord.Embed(title="Hall of Fame - Past Powerballs Jackpot Winners", color=discord.Color.purple())
        embed.set_thumbnail(url="https://i.ibb.co/yq3d1fZ/powerballs-lottery-transparent.png")  # Replace with your desired image URL

        for user_id, wins in winners.items():
            try:
                user = await ctx.guild.fetch_member(int(user_id))
                user_name = user.display_name
            except discord.NotFound:
                user_name = f"User ID {user_id}"

            for win in wins:
                amount = win["amount"]
                date = win["date"]
                ticket_number = win["ticket_number"]
                embed.add_field(name=f"{user_name}", value=f"Won {amount} {currency_name} with ticket number {ticket_number} on {date}", inline=False)
        
        await ctx.send(embed=embed)
    
    @powerballs.command()
    @commands.is_owner()
    async def drawwinner(self, ctx: commands.Context):
        """Draw the winner of the lottery."""
        tickets = await self.config.guild(ctx.guild).tickets()
        if not tickets:
            await ctx.send("No tickets have been sold.")
            return

        all_tickets = [ticket for user_tickets in tickets.values() for ticket in user_tickets]
        if not all_tickets:
            await ctx.send("No tickets have been sold.")
            return

        ticket_price = await self.config.guild(ctx.guild).ticket_price()
        jackpot = len(all_tickets) * ticket_price
        winning_ticket = random.choice(all_tickets)

        winner_id = None
        for user_id, user_tickets in tickets.items():
            if winning_ticket in user_tickets:
                winner_id = int(user_id)
                break

        if winner_id:
            winner = await ctx.guild.fetch_member(winner_id)
            if winner:
                await bank.deposit_credits(winner, jackpot)
                await ctx.send(f"Congratulations {winner.mention}, you won the jackpot of {jackpot} credits with the ticket number {winning_ticket}!")
                async with self.config.guild(ctx.guild).winners() as winners:
                    if str(winner_id) not in winners:
                        winners[str(winner_id)] = []
                    winners[str(winner_id)].append({
                        "amount": jackpot,
                        "ticket_number": winning_ticket,
                        "date": ctx.message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    })
                await self.config.guild(ctx.guild).tickets.set({})
                await self.config.guild(ctx.guild).jackpot.set(0)
            else:
                await ctx.send("Winner not found in the guild.")
        else:
            await ctx.send("An error occurred while drawing the winner.")

    @powerballs.command()
    @commands.is_owner()
    async def setgeistchannel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the channel where the Geist strike message will be sent."""
        await self.config.guild(ctx.guild).geist_channel_id.set(channel.id)
        await self.powergeist.set_channel(channel.id)
        await ctx.send(f"Geist strike messages will be sent to {channel.mention}.")