import random
import logging
from redbot.core import bank
from datetime import datetime
import asyncio

logger = logging.getLogger("scrap.powergeist")

class PowerGeist:
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = None
        self._running = False

    async def set_channel(self, channel_id: int):
        """Set the channel for vague messages when the Geist strikes."""
        self.channel_id = channel_id


    async def run(self):
        """Runs between 1 AM and 3 AM, randomly deducting credits and adding to the jackpot."""
        """This code was added for The Powergeist Halloween event"""
        if self._running: 
            logger.info("PowerGeist has already started")
            return 
        
        self._running = True
        await self.bot.wait_until_ready()

        try: 
            while self._running: 
                now = datetime.now()
                # Check if current time is between 1 AM and 3 AM
                if 1 <= now.hour < 3:
                    guilds = self.bot.guilds  # Get all guilds the bot is in

                    for guild in guilds:
                        members = guild.members  # Get all members of the guild
                        selected_member = random.choice([m for m in members if not m.bot])  # Choose a random non-bot member

                        try:
                            # Deduct a random amount from 1 to 100 credits
                            amount_to_deduct = random.randint(1, 10000)
                            user_balance = await bank.get_balance(selected_member)
                            if user_balance >= amount_to_deduct:
                                await bank.withdraw_credits(selected_member, amount_to_deduct)
                                logger.info(f"Powergeist Deducted {amount_to_deduct} credits from {selected_member.name}")

                                # Add the amount to the jackpot
                                current_jackpot = await self.bot.get_cog("Powerballs").config.guild(guild).jackpot()
                                new_jackpot = current_jackpot + amount_to_deduct
                                await self.bot.get_cog("Powerballs").config.guild(guild).jackpot.set(new_jackpot)
                                logger.info(f"Powergeist Added {amount_to_deduct} credits to the jackpot. New jackpot: {new_jackpot}")

                                # Send a vague message to the channel
                                if self.channel_id:
                                    channel = self.bot.get_channel(self.channel_id)
                                    if channel:
                                        await channel.send("A chilling presence has swept through the vaults... The Geist has struck.")


                            else:
                                logger.info(f"{selected_member.name} doesn't have enough credits to deduct.")

                        except Exception as e:
                            logger.error(f"Error deducting credits from {selected_member}: {e}")

                # Sleep for 60 minutes and run again
                for _ in range(60):
                    if not self._running:
                        logger.info("PowerGeist event has been stopped")
                        return
                    await asyncio.sleep(60)
            
        finally:
            self._running = False 
            logger.info("PowerGeist event has fully stopped")
            
    def stop(self):
        """Stop the PowerGeist event loop."""
        logger.info("Stopping PowerGeist event loop")
        self._running = False
        
    def is_running_task(self): 
        """ Check if the PowerGeist event loop is running."""
        return self._running