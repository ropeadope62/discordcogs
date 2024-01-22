import discord
from redbot.core import commands
import random
import asyncio
import random
import string

class AcroCat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_acronym = None
        self.responses = {}
        self.votes = {}

    @commands.command()
    async def acrocat(self, ctx):
        self.current_acronym = self.generate_acronym()
        embed = discord.Embed(title="Acrocat - The Best Acro Cog for Discord.", description=f"Your acronym is: `{self.current_acronym}`")
        await ctx.send(embed=embed)
        await self.start_voting(ctx)
        await asyncio.sleep(30)
        

    def generate_acronym():
        characters = []
        for _ in range(random.randint(3, 6)):
            characters.append(random.choice(string.ascii_letters))
        return characters

    acronym_template = generate_acronym()

    @commands.Cog.listener()
    async def on_message(self,ctx, message):
        if message.content.lower() == self.current_acronym.lower():
            # Perform action when the message matches the acronym exactly
            pass
        else:
            words = message.content.split()
            acronym_letters = [word[0].lower() for word in words]
            if ''.join(acronym_letters) == self.current_acronym.lower():
                # Add player's acronym to a numbered list in an embed
                player_acronym = ''.join(acronym_letters).upper()
                embed = discord.Embed(title="Acrocat - Current Entries")
                embed.add_field(name="1.", value=player_acronym, inline=False)
                await ctx.send(embed=embed)
                
    
    async def start_voting(self, ctx):
        embed = discord.Embed(title="Acrocat - Current Entries")
        for index, acronym in enumerate(self.responses.values(), start=1):
            embed.add_field(name=f"{index}.", value=acronym, inline=False)
            message = await ctx.send(embed=embed)

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            response = await self.bot.wait_for('message', check=check, timeout=30)
            vote = int(response.content)
            if vote in range(1, len(self.responses) + 1):
                if vote in self.votes:
                    self.votes[vote] += 1
                else:
                    self.votes[vote] = 1
                await ctx.send(f"{message.author}'s vote has been recorded.")
            else:
                await ctx.send("Invalid vote. Please enter a number between 1 and {len(self.responses)}.")
        except asyncio.TimeoutError:
            await ctx.send("Voting time has expired.")

   