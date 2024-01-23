import discord
from redbot.core import commands
import random
import asyncio
import string
import os

class AcroCat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_acronym = None
        self.responses = {}
        self.votes = {}
        self.min_acro_length = 3
        self.max_acro_length = 6

    @commands.group()
    async def acrocat(self, ctx: commands.Context):
        if ctx.invoked.subcommand is None:
            self.current_acronym = self.generate_acronym()
            embed = discord.Embed(title="Acrocat - The Cat's Ass of Acro Cogs. Period.", description=f"Your acronym is: `{self.current_acronym}`")
            
            # Get the path to the image file
            image_path = os.path.join(os.path.dirname(__file__), "acrocat_logo.png")
            embed.add_field(name = 'About', value='Another stupid discord cog by Slurms Mackenzie/ropeadope62' )
            embed.add_field(name = 'Repo', value='If you liked this, try my other stupid cogs! https://github.com/ropeadope62/discordcogs' )
            # Set the image in the embed
            embed.set_image(url="attachment://acrocat_logo.png")
            
            # Send the embed with the image
            await ctx.send(embed=embed, file=discord.File(image_path, "acrocat_logo.png"))
            
            await self.start_voting(ctx)
            await asyncio.sleep(30)
        

    @staticmethod
    def generate_acronym():
        return ''.join(random.choice(string.ascii_uppercase) for _ in range(random.randint(3, 6)))

    @acrocat.command(name="limits")
    @commands.is_owner()  # Ensure only the bot owner can change the limits
    async def set_limits(self, ctx, min_length: int, max_length: int):
        if 1 <= min_length <= max_length:
            self.min_length = min_length
            self.max_length = max_length
            await ctx.send(f"Acronym length limits set to {min_length}-{max_length}.")
        else:
            await ctx.send("Invalid limits. Ensure that `min_length` is at least 1 and `max_length` is greater than or equal to `min_length`.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.current_acronym and not message.author.bot and ''.join(word[0].lower() for word in message.content.split() if word) == self.current_acronym.lower():
            self.responses[message.author] = message.content

                    
        
        async def start_voting(self, ctx):
            # Creating an embed with all the responses
            embed = discord.Embed(title="Acrocat - Current Entries")
            for index, (author, acronym) in enumerate(self.responses.items(), start=1):
                embed.add_field(name=f"{index}.", value=f"{acronym} by {author.display_name}", inline=False)
        
        # Sending the embed only once after it's fully populated
        voting_message = await ctx.send(embed=embed)

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            response = await self.bot.wait_for('message', check=check, timeout=30)
            vote = int(response.content)
            if 1 <= vote <= len(self.responses):
                voted_author = list(self.responses.keys())[vote - 1]
                self.votes[voted_author] = self.votes.get(voted_author, 0) + 1
                await ctx.send(f"{response.author.display_name}'s vote has been recorded.")
            else:
                await ctx.send(f"Invalid vote. Please enter a number between 1 and {len(self.responses)}.")
        except asyncio.TimeoutError:
            await ctx.send("Voting time has expired.")
        
        # Creating an embed with all the votes
        embed = discord.Embed(title="Acrocat - Current Votes")
        for index, (author, votes) in enumerate(self.votes.items(), start=1):
            embed.add_field(name=f"{index}.", value=f"{author.display_name}: {votes}", inline=False)
        await ctx.send(embed=embed)
        
    