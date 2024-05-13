import discord
from redbot.core import commands,bank
from redbot.core import Config
import random
import asyncio
import string
import os
from collections import Counter, defaultdict 
from contextlib import suppress


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
        default_guild_settings = ({"min_acro_length": 3, 
                                   "max_acro_length": 5,
                                   "submission_timer": 30,
                                   "voting_timer": 30, 
                                   "acro_isanon": False, 
                                   "min_reward": 10, 
                                   "max_reward": 100,
                                   "weighted_chars": False, 
                                   "rewards": True})
        default_user_settings = ({"acros_submitted": 0, 
                                   "wins": 0,
                                   "most_voted_acronym": None,
                                   "most_votes": 0, 
                                   "winnings": 0})
        self.config.register_guild(**default_guild_settings)
        self.config.register_user(**default_user_settings)
    
    @commands.command()
    async def acrocat(self, ctx: commands.Context, *letters: str):
        if self.game_state is not None:
            await ctx.send("Another game is already in progress. Please wait for the current game to end.")
            return
        self.voting_channel = ctx.channel
        self.game_state = 'collecting'
        min_length = await self.config.guild(ctx.guild).min_acro_length()
        max_length = await self.config.guild(ctx.guild).max_acro_length()
        if letters:  # If letters are provided
            if not all(letter.isalpha() and len(letter) == 1 for letter in letters):
                await ctx.send("Invalid letters. Please provide single, alphabetical characters.")
                await self.reset_gamestate()  # Ensure async function is awaited
                return
            if len(letters) < min_length or len(letters) > max_length:
                await ctx.send(f"The length of the acronym must be between {min_length} and {max_length} characters long.")
                await self.reset_gamestate()  # Ensure async function is awaited
                return
            self.current_acronym = "".join(letters).upper()
        else:  # If no letters provided, generate the acronym automatically
            self.current_acronym = await self.generate_acronym(ctx)
        embed = discord.Embed(
            title="Acrocat - The Cat's Ass of Acro Cogs.",
            description=f"Your acronym is: **`{self.current_acronym}`**",
            color=discord.Color.orange()
        )

        image_path = os.path.join(os.path.dirname(__file__), "acrocat_logo.png")
        embed.set_thumbnail(url="attachment://acrocat_logo.png")

        message = await ctx.send(embed=embed, file=discord.File(image_path, "acrocat_logo.png"))
        submission_timer_value = await self.config.guild(ctx.guild).submission_timer()
        for i in range(submission_timer_value, 0, -1):
            await asyncio.sleep(1)
            embed.description = f"Your acronym is: **`{self.current_acronym}`**\nCountdown: {i}"
            await message.edit(embed=embed)

        await self.start_voting(ctx)

    async def start_voting(self, ctx):
        self.game_state = 'voting'
        print(f'starting voting in {ctx.channel}')
        self.voting_channel = ctx.channel
        voting_countdown = await self.config.guild(ctx.guild).voting_timer()
        

        if not self.responses:
            await ctx.send("No responses were submitted. Ending the game.")
            await self.reset_gamestate()
            return

        if len(self.responses) == 1:
            winning_author, winning_response = next(iter(self.responses.items()))
            await ctx.send(f"{winning_author.display_name} is playing with themselves. They submitted: {winning_response}")
            await self.reset_gamestate()
            return
        is_anon = await self.config.guild(ctx.guild).acro_isanon()
        embed = discord.Embed(title="Vote for your favorite response!", description=f"{voting_countdown} seconds remaining", color=discord.Color.orange())
        for index, (author, response) in enumerate(self.responses.items(), start=1):
            if is_anon == True: 
                embed.add_field(name=f"Option {index}", value=f"{response}", inline=False)
            else: 
                embed.add_field(name=f"Option {index}", value=f"{response} by {author.display_name}", inline=False)
        voting_message = await ctx.send(embed=embed)
        
        for remaining in range(voting_countdown, 0, -1):
            await asyncio.sleep(1)  # Wait for 1 second
            new_embed = discord.Embed(title="Vote for your favorite response!", description=f"{remaining} seconds remaining", color=discord.Color.orange())
            for index, (author, response) in enumerate(self.responses.items(), start=1):
                if is_anon == True:
                    new_embed.add_field(name=f"Option {index}", value=f"{response}", inline=False)
                else:
                    new_embed.add_field(name=f"Option {index}", value=f"{response} by {author.display_name}", inline=False)
            await voting_message.edit(embed=new_embed)
            
        await self.tally_votes(ctx)

    async def update_stats(self, winning_author, winning_response, reward, votes_for_winning_response):
        user_data = await self.config.user(winning_author).all()
        user_data['wins'] += 1
        user_data['winnings'] += reward
        if votes_for_winning_response > user_data.get('most_votes', 0):
            user_data['most_voted_acronym'] = winning_response
            user_data['most_votes'] = votes_for_winning_response

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
                value="Another stupid discord cog by Slurms Mackenzie/ropeadope62\n Use [p]acrocatstat for stats or [p]acrocatstat leaderboard to show the leaderboard", inline="True"
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
                value=f"{await self.config.guild(ctx.guild).voting_timer()}", inline="False"
            )
            embed.add_field(
                name="Submission Countdown:",
                value=f"{await self.config.guild(ctx.guild).submission_timer()}", inline="False"
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
    
    @acrocatset.command(name="letters", description="Set the minimum and maximum length of the acronym.")
    @commands.has_permissions(manage_guild=True)
    @commands.is_owner()
    async def set_letter_limits(self, ctx, min_length: int, max_length: int):
        if min_length > max_length:
            await ctx.send("Invalid limits. Ensure that `min_length` is less than or equal to `max_length`.")
            return
        await self.config.guild(ctx.guild).min_acro_length.set(min_length)
        await self.config.guild(ctx.guild).max_acro_length.set(max_length)
        await ctx.send(f"Acronym length limits set to {min_length}-{max_length}.")
    
    @acrocatset.command(name="votingcountdown", description="Set the voting timeout in seconds.")
    @commands.has_permissions(manage_guild=True)
    @commands.is_owner()
    async def set_voting_timeout(self, ctx, timeout: int):
        if timeout >= 10:
            await self.config.guild(ctx.guild).voting_timer.set(timeout)
            await ctx.send(f"Voting timeout set to {timeout} seconds.")
        else:
            await ctx.send("Invalid timeout. Ensure that `timeout` is at least 10 seconds.")
            
    @acrocatset.command(name="submissioncountdown", description="Set the submission timeout in seconds.")
    @commands.has_permissions(manage_guild=True)
    @commands.is_owner()
    async def set_submission_timeout(self, ctx, timeout: int):
        if timeout >= 10:
            await self.config.guild(ctx.guild).submission_timer.set(timeout)
            await ctx.send(f"Submission timeout set to {timeout} seconds.")
        else:
            await ctx.send("Invalid timeout. Ensure that `timeout` is at least 10 seconds.")
                    
    
    
    @acrocatset.command(name="weightedletters", description="Toggle weighted letters for acronyms. When enabled, there will be less occurences of less common letters.")
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
            
    @acrocatset.command(name="rewards", description="Toggle rewards for winning acronyms.")
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
            
    @acrocatset.command(name="rewardrange", description= "Set the reward range for each letter submitted.")
    @commands.has_permissions(manage_guild=True)
    @commands.is_owner()
    async def set_reward_range(self, ctx, min_reward: int, max_reward: int):
        if min_reward > max_reward:
            await ctx.send("Invalid reward range. Ensure that `min_reward` is less than or equal to `max_reward`.")
            return
        await self.config.guild(ctx.guild).min_reward.set(min_reward)
        await self.config.guild(ctx.guild).max_reward.set(max_reward)
        await ctx.send(f"Reward range set to {min_reward}-{max_reward}.")
    
    @acrocatset.command(name="anon", description= "Toggle anonymous submissions. When enabled, acro submissions will be anonymous.")
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

        if not vote_counts:
            await ctx.send("No votes were cast. Ending the game.")
            await self.reset_gamestate()
            return

        max_votes = max(vote_counts.values(), default=0)
        winning_indices = [index for index, count in vote_counts.items() if count == max_votes]

        response_authors = list(self.responses.keys())
        winning_responses = {response_authors[index]: self.responses[response_authors[index]] for index in winning_indices if index < len(response_authors)}

        if not winning_responses:
            await ctx.send("Error: Could not determine winning responses.")
            await self.reset_gamestate()
            return
        if len(winning_responses) > 1:
            winners_message = "It's a tie! The winning submissions are:\n"
            split_reward = reward // len(winning_responses)
            for author, response in winning_responses.items():
                winners_message += f"{author.display_name}: {response}\n"
                await bank.deposit_credits(author, split_reward)
                await self.update_stats(author, response, split_reward, max_votes)
            await ctx.send(winners_message + f"Each winner has been awarded {split_reward} {currency_name} for playing!")
        else:
            winning_author = list(winning_responses.keys())[0]
            winning_response = winning_responses[winning_author]
            await bank.deposit_credits(winning_author, reward)
            await ctx.send(f"The winner is {winning_author.display_name} with the response: {winning_response}. They have been awarded {reward} {currency_name}!")
            await self.update_stats(winning_author, winning_response, reward, max_votes)

        await self.reset_gamestate()
        
    
    
    @commands.group(name="acrocatstat")
    async def acrocatstat(self, ctx):
        if ctx.subcommand_passed is None:
            user_data = await self.config.user(ctx.author).all()
            wins = user_data['wins']
            acros_submitted = user_data['acros_submitted']
            most_voted_acronym = user_data['most_voted_acronym'] or 'N/A'
            await ctx.send(f"{ctx.author.display_name}, you have made {acros_submitted} acronyms and won {wins} times. Your most voted acronym was: {most_voted_acronym}")
    
    @acrocatstat.command(name="leaderboard")
    async def acrocat_leaderboard(self, ctx):
        all_users_data = await self.config.all_users()
        sorted_users = sorted(all_users_data.items(), key=lambda x: x[1]['wins'], reverse=True)

        # Prepare leaderboard message
        leaderboard_message = ""
        for i, (user, data) in enumerate(sorted_users, start=1):
            user_obj = await self.bot.fetch_user(user)  # Fetch User object to get display name
            leaderboard_message += f"{i}. {user_obj.display_name} - {data['wins']} wins - {data['winnings']} boofcoin\n"

        # Create embed
        embed = discord.Embed(title="Acrocat Leaderboard", description=leaderboard_message, color=discord.Color.orange())
        embed.set_thumbnail(url="attachment://acrocat_logo.png")

        # Send leaderboard message
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or self.game_state not in ['collecting', 'voting'] or message.channel != self.voting_channel:
            return

        print(f'game state is {self.game_state}')

        if self.current_acronym and self.game_state == 'collecting':
            acro_check = "".join(word[0].lower() for word in message.content.split() if word) == self.current_acronym.lower()
            if acro_check:
                self.responses[message.author] = message.content
                acros_submitted = await self.config.user(message.author).acros_submitted()
                await self.config.user(message.author).acros_submitted.set(acros_submitted + 1)
                try:
                    await message.delete()
                    print(f'Deleting message from {message.author}')
                except (discord.Forbidden, discord.HTTPException) as e:
                    print(f"Failed to delete the message: {e}")

        elif self.game_state == 'voting':
            try:
                vote_index = int(message.content.strip()) - 1
                if 0 <= vote_index < len(self.responses):
                    if message.author in self.votes:
                        await message.channel.send(f"{message.author.display_name}, you have already voted.")
                        return
                    response_authors = list(self.responses.keys())
                    response_author = response_authors[vote_index]
                    if message.author == response_author:
                        await message.channel.send(f"{message.author.display_name} attempted to vote for themselves! Nice Try!")
                        return
                    # Record the vote
                    self.votes[message.author] = vote_index
                    await message.delete()
                    await message.channel.send(f"{message.author.display_name}, your vote has been recorded.")
                else:
                    await message.channel.send("Invalid vote. Please select a valid option.")
            except ValueError:
                # Handle the case where the message isn't a valid integer
                return
