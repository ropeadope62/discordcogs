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
        self.name_with_acro = 0

    async def start_voting(self, ctx):
        if not self.responses:
            await ctx.send("Waiting for player responses...")
            return

        embed = discord.Embed(title="Acrocat - Vote for the Best Acronym!")
        for index, (author, response) in enumerate(self.responses.items(), start=1):
            if self.name_with_acro == 1:
                embed.add_field(name=f"{index}.", value=f"{response} by {author.display_name}", inline=False)
            embed.add_field(name=f"{index}.", value=f"{response}", inline=False)
        voting_message = await ctx.send(embed=embed)
        self.responses = {}
        self.votes = {}


    @commands.group()
    async def acrocat(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            self.current_acronym = self.generate_acronym()
            embed = discord.Embed(
                title="Acrocat - The Cat's Ass of Acro Cogs.",
                description=f"Your acronym is: **`{self.current_acronym}`**",
            )
            
            image_path = os.path.join(os.path.dirname(__file__), "acrocat_logo.png")
            embed.add_field(
                name="About",
                value="Another stupid discord cog by Slurms Mackenzie/ropeadope62",
            )
            embed.add_field(
                name="Repo",
                value="If you liked this, try my other stupid cogs! https://github.com/ropeadope62/discordcogs",
            )
            embed.set_image(url="attachment://acrocat_logo.png")
            
            await ctx.send(
                embed=embed, file=discord.File(image_path, "acrocat_logo.png")
            )
            await asyncio.sleep(30)
            await self.start_voting(ctx)

    @staticmethod
    def generate_acronym():
        return "".join(
            random.choice(string.ascii_uppercase + '.') for _ in range(random.randint(3, 6))
        )

    @acrocat.command(name="limits")
    @commands.is_owner()  # Ensure only the bot owner can change the limits
    async def set_limits(self, ctx, min_length: int, max_length: int):
        if 1 <= min_length <= max_length:
            self.min_length = min_length
            self.max_length = max_length
            await ctx.send(f"Acronym length limits set to {min_length}-{max_length}.")
        else:
            await ctx.send(
                "Invalid limits. Ensure that `min_length` is at least 1 and `max_length` is greater than or equal to `min_length`."
            )

    
    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            self.current_acronym
            and not message.author.bot
            and "".join(word[0].lower() for word in message.content.split() if word)
            == self.current_acronym.lower()
        ):
            self.responses[message.author] = message.content
            try:
                await message.delete()  # Delete the message to keep the submission anonymous
            except discord.Forbidden:
                print("Bot does not have permissions to delete messages.")
            except discord.HTTPException:
                print("Deleting the message failed.")
