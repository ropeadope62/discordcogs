import discord
from redbot.core import commands
import random
import asyncio
import string
import os
from collections import Counter


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



    @commands.command()
    embed.set_image(url="attachment://acrocat_logo.png", width=276, height=94)

    async def start_voting(self, ctx):
        self.game_state = 'voting'
        print(f'starting voting in {ctx.channel}')
        self.voting_channel = ctx.channel
        if not self.responses:
            print(f'waiting for players responses')
            await ctx.send("Waiting for player responses...")
            return

        # Display voting options
        embed = discord.Embed(title="Vote for your favorite!")
        for index, (author, response) in enumerate(self.responses.items(), start=1):
            display_name = f"{response} by {author.display_name}" if self.name_with_acro == 1 else response
            embed.add_field(name=f"{index}.", value=display_name, inline=False)
        
        voting_message = await ctx.send(embed=embed)
        self.voting_message_id = voting_message.id
        print(f'storing voting message id {self.voting_message_id}')
        print(f'storing voting channel {self.voting_channel}')

        # Wait 30 seconds for voting
        await asyncio.sleep(30)

        # Tally votes and announce the winner
        await self.tally_votes(ctx)

        # Reset game state and other variables for the next round
        self.game_state = None
        self.responses = {}
        self.votes = {}
        self.voting_channel = None


    @staticmethod
    def generate_acronym():
        return "".join(random.choice(string.ascii_uppercase) for _ in range(random.randint(3, 6)))

    @commands.command(name="letters")
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
            
    async def tally_votes(self, ctx):
        vote_counts = Counter(self.votes.values())
        winning_vote = vote_counts.most_common(1)
        if winning_vote:
            winning_index = winning_vote[0][0]
            winning_author, winning_response = list(self.responses.items())[winning_index - 1]
            await ctx.send(f"The winner is {winning_author.display_name} with the response: {winning_response}")
        else:
            await ctx.send("No votes were cast.")

    @commands.Cog.listener()
    async def on_message(self, message):
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
            try:
                vote = int(message.content.strip())
                if 1 <= vote <= len(self.responses):
                    response_author = list(self.responses.keys())[vote - 1]
                    if message.author != response_author:
                        self.votes[message.author] = vote
                    else:
                        await message.channel.send(f"You cannot vote for your own response, {message.author.display_name}.")
                await message.delete()
            except (ValueError, IndexError):
                pass


