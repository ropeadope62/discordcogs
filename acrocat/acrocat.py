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

    @commands.command()
    async def acrocat(self, ctx: commands.Context):
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
        characters = []
        for _ in range(random.randint(3, 6)):
            characters.append(random.choice(string.ascii_uppercase))
        return characters

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower() != self.current_acronym.lower():
            words = message.content.split()
            acronym_letters = [word[0].lower() for word in words]
            if ''.join(acronym_letters) == self.current_acronym.lower():
                # Add player's acronym to a numbered list in an embed
                player_acronym = ''.join(acronym_letters).upper()
                embed = discord.Embed(title="Acrocat - Current Entries")
                embed.add_field(name="1.", value=player_acronym, inline=False)
                await message.channel.send(embed=embed)
                
    
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
        
    