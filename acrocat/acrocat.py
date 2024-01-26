import discord
from redbot.core import commands
from redbot.core import Config
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
        self.config = Config.get_conf(self, identifier=94859234884920455, force_registration=True)
        self.config.register_user(acros_submitted=0, wins=0, most_voted_acronym=None, most_votes=0)



    @commands.command()
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

            for i in range(45, 0, -1):
                await asyncio.sleep(1)
                embed.description = f"Your acronym is: **`{self.current_acronym}`**\nCountdown: {i}"
                await message.edit(embed=embed)

            await self.start_voting(ctx)

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
            message = await ctx.send(embed=embed)
        for i in range(45, 0, -1):
                await asyncio.sleep(1)
                embed.description = f"Your acronym is: **`{self.current_acronym}`**\nCountdown: {i}"
                await message.edit(embed=embed)
                
        voting_message = await ctx.send(embed=embed)
        self.voting_message_id = voting_message.id
        print(f'storing voting message id {self.voting_message_id}')
        print(f'storing voting channel {self.voting_channel}')

        # Wait 30 seconds for voting
        await asyncio.sleep(30)

        # Tally votes and announce the winner
        await self.tally_votes(ctx)

    async def update_stats(self, winner, winning_acronym):
        user_data = await self.config.user(winner).all()
        user_data['wins'] += 1
        current_votes = self.votes.values().count(winner)
        if current_votes > user_data['most_votes']:
            user_data['most_voted_acronym'] = winning_acronym
            user_data['most_votes'] = current_votes

        await self.config.user(winner).set(user_data)
        
    async def reset_gamestate(self):   
        self.game_state = None
        self.responses = {}
        self.votes = {}
        self.voting_channel = None
        
        await self.reset_gamestate()

    @staticmethod
    def generate_acronym():
        return "".join(random.choice(string.ascii_uppercase) for _ in range(random.randint(3, 6)))

    
    @commands.group()
    @commands.has_permissions(manage_guild=True)
    async def acrocatset(self, ctx): 
        """Settings for Acrocat."""
        pass
    
    @acrocatset.command(name="letters")
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
            winning_author, winning_response = list(self.responses.items())[winning_vote - 1]
            await ctx.send(f"The winner is {winning_author.display_name} with the response: {winning_response}")
            await self.update_stats(winning_author, winning_response)
        else:
            await ctx.send("No votes were cast.")
    
    @commands.command(name="acrocatstat")
    async def get_stats(self, ctx):
        user_data = await self.config.user(ctx.author).all()
        wins = user_data['wins']
        acros_submitted = user_data['acros_submitted']
        most_voted_acronym = user_data['most_voted_acronym'] or 'N/A'
        await ctx.send(f"{ctx.author.display_name}, you have made {acros_submitted} acronyms and won {wins} times. Your most voted acronym was: {most_voted_acronym}")

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
                acros_submitted = await self.config.user(message.author).acros_submitted()
                await self.config.user(message.author).acros_submitted.set(acros_submitted + 1)
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
                    if message.author == response_author:
                        await message.channel.send(f"You cannot vote for your own response, {message.author.display_name}.")
                        return
                    if message.author in self.votes:
                        await message.channel.send(f"{message.author.display_name}, you have already voted.")
                    else:
                        self.votes[message.author] = vote
                        await message.channel.send(f"Vote recorded for {message.author.display_name}.")
                        
                    await message.delete()
            except (ValueError, IndexError):
                pass

