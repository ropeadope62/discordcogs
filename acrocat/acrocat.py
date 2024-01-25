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
        self.game_state = None
        self.voting_channel = None



    @commands.group()
    async def acrocat(self, ctx: commands.Context):
        self.game_state = 'collecting'
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
                value="If you liked this, check out my other cogs! https://github.com/ropeadope62/discordcogs",
            )
            embed.set_image(url="attachment://acrocat_logo.png")

            message = await ctx.send(embed=embed, file=discord.File(image_path, "acrocat_logo.png"))

            for i in range(30, 0, -1):
                await asyncio.sleep(1)
                embed.description = f"Your acronym is: **`{self.current_acronym}`**\nCountdown: {i}"
                await message.edit(embed=embed)

            await self.start_voting(ctx)

    async def start_voting(self, ctx):
        self.game_state = 'voting'
        print(f'starting voting in {ctx.channel}')
        self.voting_channel = ctx.channel
        print(f'game state is {self.game_state}')
        if not self.responses:
            print(f'waiting for players responses')
            await ctx.send("Waiting for player responses...")
            return
        embed = discord.Embed(title="Vote for your favorite!")
        for index, (author, response) in enumerate(self.responses.items(), start=1):
            if self.name_with_acro == 1:
                print(f'adding {index} {response} by {author.display_name}')
                embed.add_field(name=f"{index}.", value=f"{response} by {author.display_name}", inline=False)
            else:
                embed.add_field(name=f"{index}.", value=f"{response}", inline=False)
        voting_message = await ctx.send(embed=embed)
        self.voting_message_id = voting_message.id
        print(f'storing voting message id {self.voting_message_id}')
        print(f'storing voting channel {self.voting_channel}')
        self.responses = {}


    @staticmethod
    def generate_acronym():
        return "".join(random.choice(string.ascii_uppercase) for _ in range(random.randint(3, 6)))

    @acrocat.command(name="letters")
    @commands.has_permissions(manage_guild=True)
    @commands.is_owner()
    async def set_letter_limits(self, ctx, min_length: int, max_length: int):
        if 1 <= min_length <= max_length:
            self.min_acro_length = min_length
            self.max_acro_length = max_length
            await ctx.send(f"Acronym length limits set to {min_length}-{max_length}.")
        else:
            await ctx.send(
                "Invalid limits. Ensure that `min_length` is at least 1 and `max_length` is greater than or equal to `min_length`."
            )
            
    async def end_vote(self, ctx):
        if self.game_state != 'voting':
            await ctx.send("Voting is not currently active.")
            return

        # Tally the votes
        vote_counts = {index: 0 for index in range(1, len(self.responses) + 1)}
        for vote in self.votes.values():
            if vote in vote_counts:
                vote_counts[vote] += 1

        if not vote_counts:
            await ctx.send("No votes were cast.")
            self.game_state = None
            return

        # Determine the winner
        winning_vote = max(vote_counts, key=vote_counts.get)
        winner_response = list(self.responses.values())[winning_vote - 1]
        winner_user = list(self.responses.keys())[winning_vote - 1]
        await ctx.send(f"The winner is {winner_user.display_name} with the response: {winner_response}")
        self.game_state = None
        self.current_acronym = None
        self.responses = {}
        self.votes = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.channel != self.voting_channel:
            return
        if self.game_state == 'collecting':
            print(f'game state is {self.game_state}')
            is_valid_acronym = (
                self.current_acronym
                and "".join(word[0].lower() for word in message.content.split() if word) == self.current_acronym.lower()
            )

            if is_valid_acronym:
                print(f'found valid acronym from {message.author}')
                self.responses[message.author] = message.content
                try:
                    await message.delete()                   
                    print(f'Deleting message from {message.author}')
                except discord.Forbidden:
                    print("Bot does not have permissions to delete messages.")
                except discord.HTTPException:
                    print("Deleting the message failed.")

        elif self.game_state == 'voting':
            print(f'game state is {self.game_state}')
            try:
                vote = int(message.content.strip())
                if 1 <= vote <= len(self.responses):
                    print(f'determined vote is {vote}')
                    print(f'vote from {message.author} for {vote}')
                    self.votes[message.author] = vote
                    await message.add_reaction("✅")
                    await message.delete()
            except ValueError:
                print("Deleting the message failed.")


