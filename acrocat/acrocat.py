import discord
from redbot.core import commands,bank
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
        self.name_with_acro = 0
        self.game_state = None
        self.voting_channel = None
        self.config = Config.get_conf(self, identifier=94859234884920455, force_registration=True)
        self.config.register_guild(min_acro_length=3, 
                                   max_acro_length=6, 
                                   timer=30, 
                                   acro_isanon=False, 
                                   min_reward=None, 
                                   max_reward=None,
                                   weighted_chars=False, 
                                   rewards=True)
        self.config.register_user(acros_submitted=0, wins=0, most_voted_acronym=None, most_votes=0, winnings=0)


    @commands.command()
    async def acrocat(self, ctx: commands.Context):
        if self.game_state is not None:
            await ctx.send("Another game is already in progress. Please wait for the current game to end.")
            return
        self.game_state = 'collecting'
        if ctx.invoked_subcommand is None:
            self.current_acronym = await self.generate_acronym(ctx)
            embed = discord.Embed(
                title="Acrocat - The Cat's Ass of Acro Cogs.",
                description=f"Your acronym is: **`{self.current_acronym}`**",
                color=discord.Color.orange()
            )

            image_path = os.path.join(os.path.dirname(__file__), "acrocat_logo.png")
            embed.set_thumbnail(url="attachment://acrocat_logo.png")

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
        voting_countdown = await self.config.guild(ctx.guild).timer()

        if not self.responses:
            await ctx.send("No responses were submitted. Ending the game.")
            await self.reset_gamestate()
            return

        if len(self.responses) == 1:
            winning_author, winning_acronym = list(self.responses.items())[0]
            await ctx.send(f"{winning_author.display_name} is playing with themselves since no one else made a submission. Too bad. Their acronym was: {winning_acronym}")
            await self.update_stats(winning_author, winning_acronym, reward=0)
            await self.reset_gamestate()
            return
        is_anon = await self.config.guild(ctx.guild).acro_isanon()
        timer_value = await self.config.guild(ctx.guild).timer()
        embed = discord.Embed(title="Vote for your favorite response!", description=f"{timer_value} seconds remaining")
        for index, (author, response) in enumerate(self.responses.items(), start=1):
            if is_anon == True: 
                embed.add_field(name=f"Option {index}", value=f"{response}", inline=False)
            else: 
                embed.add_field(name=f"Option {index}", value=f"{response} by {author.display_name}", inline=False)
        voting_message = await ctx.send(embed=embed)
        
        for remaining in range(self.voting_countdown, 0, -1):
            await asyncio.sleep(1)  # Wait for 1 second
            new_embed = discord.Embed(title="Vote for your favorite response!", description=f"{remaining} seconds remaining")
            for index, (author, response) in enumerate(self.responses.items(), start=1):
                if is_anon == True:
                    new_embed.add_field(name=f"Option {index}", value=f"{response}", inline=False)
                else:
                    new_embed.add_field(name=f"Option {index}", value=f"{response} by {author.display_name}", inline=False)
            await voting_message.edit(embed=new_embed)
            
        await self.tally_votes(ctx)

    async def update_stats(self, winning_author, winning_acronym, reward):
        user_data = await self.config.user(winning_author).all()
        user_data['wins'] += 1
        user_data['winnings'] += reward
        current_votes = list(self.votes.values()).count(winning_acronym)
        if current_votes > user_data['most_votes']:
            user_data['most_voted_acronym'] = winning_acronym
            user_data['most_votes'] = current_votes

        await self.config.user(winning_author).set(user_data)
        
    async def reset_gamestate(self):   
        self.game_state = None
        self.responses = {}
        self.votes = {}
        self.voting_channel = None


    async def generate_acronym(self, ctx):
        min_acro_length = await self.config.guild(ctx.guild).min_acro_length()
        max_acro_length = await self.config.guild(ctx.guild).max_acro_length()
        if not await self.config.guild(ctx.guild).weighted_chars():
            return "".join(random.choice(string.ascii_uppercase) for _ in range(random.randint(min_acro_length, max_acro_length)))
        else:
            weighted_letters = (
            "A" * 9 + "B" * 2 + "C" * 2 + "D" * 4 + "E" * 12 + "F" * 2 + "G" * 3 +
            "H" * 2 + "I" * 9 + "J" * 1 + "K" * 1 + "L" * 4 + "M" * 2 + "N" * 6 +
            "O" * 8 + "P" * 2 + "Q" * 1 + "R" * 6 + "S" * 4 + "T" * 6 + "U" * 4 +
            "V" * 2 + "W" * 2 + "X" * 1 + "Y" * 2 + "Z" * 1)
        
            return "".join(random.choice(weighted_letters) for _ in range(random.randint(min_acro_length, max_acro_length)))

        
    @commands.group()
    @commands.has_permissions(manage_guild=True)
    async def acrocatset(self, ctx): 
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Acrocat - The Cat's Ass of Acro Cogs.",
                description=f"Cog Settings",
                color=discord.Color.orange()
            )

            image_path = os.path.join(os.path.dirname(__file__), "acrocat_logo.png")
            embed.add_field(
                name="About",
                value="Another stupid discord cog by Slurms Mackenzie/ropeadope62", inline="True"
            )
            embed.add_field(
                name="Repo",
                value="If you liked this, check out my other cogs! https://github.com/ropeadope62/discordcogs",inline="True"
            )
            embed.add_field(
                name="Letter Count:",
                value=f"{await self.config.guild(ctx.guild).min_acro_length()} - {await self.config.guild(ctx.guild).max_acro_length()}", inline="False")
            embed.add_field(
                name="Voting Countdown:",
                value=f"{await self.config.guild(ctx.guild).timer()}", inline="False"
            )
            embed.add_field(
                name="Weighted Letters",
                value=f"{await self.config.guild(ctx.guild).weighted_chars()}", inline="False"
            )
            embed.add_field(
                name="Anonymous Submissions",
                value=f"{await self.config.guild(ctx.guild).acro_isanon()}", inline="False"
            )
            embed.add_field(
                name="Rewards Status:",
                value=f"{await self.config.guild(ctx.guild).rewards()}", inline="False"
            )
            embed.add_field(
                name="Reward Range:",
                value=f"minimum: {await self.config.guild(ctx.guild).min_reward()} maximum: {await self.config.guild(ctx.guild).max_reward()}", inline="False"
            )
            
            embed.set_thumbnail(url="attachment://acrocat_logo.png")

            message = await ctx.send(embed=embed, file=discord.File(image_path, "acrocat_logo.png"))
    
    @acrocatset.command(name="letters")
    @commands.has_permissions(manage_guild=True)
    @commands.is_owner()
    async def set_letter_limits(self, ctx, min_length: int, max_length: int):
        if min_length > max_length:
            await ctx.send("Invalid limits. Ensure that `min_length` is less than or equal to `max_length`.")
            return
        await self.config.guild(ctx.guild).min_acro_length.set(min_length)
        await self.config.guild(ctx.guild).max_acro_length.set(max_length)
        await ctx.send(f"Acronym length limits set to {min_length}-{max_length}.")
    
    @acrocatset.command(name="timer")
    @commands.has_permissions(manage_guild=True)
    @commands.is_owner()
    async def set_voting_timeout(self, ctx, timeout: int):
        if timeout >= 10:
            self.timer = timeout
            await ctx.send(f"Voting timeout set to {timeout} seconds.")
        else:
            await ctx.send("Invalid timeout. Ensure that `timeout` is at least 10 seconds.")
            
    @acrocatset.command(name="weightedletters")
    @commands.has_permissions(manage_guild=True)
    @commands.is_owner()
    async def set_weighted_letters(self, ctx):
        weighted_chars = await self.config.guild(ctx.guild).weighted_chars()
        if weighted_chars is True:
            await self.config.guild(ctx.guild).weighted_chars.set(False)
            await ctx.send("Acrocat will no longer use weighted letters.")
        else:
            await self.config.guild(ctx.guild).weighted_chars.set(True)
            await ctx.send("Acrocat will now use weighted letters.")
            
    @acrocatset.command(name="rewards")
    @commands.has_permissions(manage_guild=True)
    @commands.is_owner()
    async def set_rewards(self, ctx):
        rewards = await self.config.guild(ctx.guild).rewards()
        if rewards:
            await self.config.guild(ctx.guild).rewards.set(False)
            await ctx.send("Acrocat rewards are now disabled.")
        else:
            await self.config.guild(ctx.guild).rewards.set(True)  # Correctly update the config here
            await ctx.send("Acrocat rewards are now enabled.")
            
    @acrocatset.command(name="rewardrange")
    @commands.has_permissions(manage_guild=True)
    @commands.is_owner()
    async def set_reward_range(self, ctx, min_reward: int, max_reward: int):
        if min_reward > max_reward:
            await ctx.send("Invalid reward range. Ensure that `min_reward` is less than or equal to `max_reward`.")
            return
        await self.config.guild(ctx.guild).min_reward.set(min_reward)
        await self.config.guild(ctx.guild).max_reward.set(max_reward)
        await ctx.send(f"Reward range set to {min_reward}-{max_reward}.")
    
    @acrocatset.command(name="anon")
    @commands.has_permissions(manage_guild=True)
    @commands.is_owner()
    async def set_anon(self, ctx):
        is_anon = await self.config.guild(ctx.guild).acro_isanon()
        if is_anon is True:
            await self.config.guild(ctx.guild).acro_isanon.set(False)
            await ctx.send("Acrocat submissions are no longer anonymous.")
        else:
            await self.config.guild(ctx.guild).acro_isanon.set(True)
            await ctx.send("Acrocat submissions are now anonymous.")
    async def tally_votes(self, ctx):
        self.game_state = 'tallying'
        min_reward = await self.config.guild(ctx.guild).min_reward()
        max_reward = await self.config.guild(ctx.guild).max_reward()
        reward = random.randint(min_reward, max_reward) * len(self.current_acronym)
        currency_name = await bank.get_currency_name(ctx.guild)
        vote_counts = Counter(self.votes.values())

        # Check if no votes were cast
        if not vote_counts:
            await ctx.send("No votes were cast. Everyone loses.")
            await self.reset_gamestate()
            return

        winning_votes = vote_counts.most_common()

        if len(winning_votes) > 1 and winning_votes[0][1] == winning_votes[1][1]:
            await ctx.send(f"It's a tie! {winning_votes[0][1]} votes each. No one wins.")
            await self.reset_gamestate()
            return

        winning_response_key = winning_votes[0][0]

        if winning_response_key in self.responses:
            winning_author = winning_votes[0][0]
            winning_acronym = self.responses[winning_author]
            if len(winning_votes) == 1:
                await ctx.send(f"{winning_author.display_name} won by default with the acro: {winning_acronym}. Too bad they are playing with themselves!")
            else:
                await bank.deposit_credits(winning_author, reward)
                await ctx.send(f"The winner is {winning_author.display_name} with the response: {winning_acronym}. They have been awarded {reward} {currency_name}!")
                await self.update_stats(winning_author, winning_acronym, reward)
        else:
            await ctx.send("Error: Winning response not found.")
            return

        await self.reset_gamestate()
    
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
                vote_index = int(message.content.strip()) - 1  # Convert to zero-based index
                if 0 <= vote_index < len(self.responses):
                    response_author = list(self.responses.keys())[vote_index]
                    if message.author == response_author:
                        await message.channel.send(f"{message.author.display_name} attempted to vote for themselves! Nice try!")
                        return
                    if message.author in self.votes:
                        await message.channel.send(f"{message.author.display_name}, you have already voted.")
                    else:
                        self.votes[message.author] = response_author  # Store the author of the response
                        await message.channel.send(f"Vote recorded for {message.author.display_name}.")
                        
                    await message.delete()
            except (ValueError, IndexError):
                pass

