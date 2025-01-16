import aiohttp
import logging
import os
import discord
import asyncio
import random 
import textwrap

from redbot.core import commands, Config, bank
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageTransform
from dotenv import load_dotenv


class MemoryLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_records = []

    def emit(self, record):
        self.log_records.append(self.format(record))

    def get_logs(self):
        return self.log_records

    def clear_logs(self):
        self.log_records = []

load_dotenv()

class CaptionCrunch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=54845646161656648796523169864)
        default_user = {
            "wins": 0, 
            "crunches": 0, 
            "most_voted_caption": None,
            "most_votes": 0,
            "winnings": 0
        }
        default_guild = {
            "captioncrunch_channel": None, 
            "nsfw_enabled": False, 
            "caption_maxlength": 70, 
            "caption_minlength": 3, 
            "submission_timeout": 30, 
            "vote_timeout": 30, 
            "caption_font_size": 52,
            "query": None,
            "rewards": True,
            "min_reward": 10,
            "max_reward": 100
        }
        
        self.config.register_user(**default_user)
        self.config.register_guild(**default_guild)
        self.setup_logging()
        self.voting_channel = None
        self.game_state = None
        self.submissions = {}
        
        
    def setup_logging(self):
        self.logger = logging.getLogger("red.captioncrunch")
        self.logger.setLevel(logging.DEBUG)

        if not any(
            isinstance(handler, MemoryLogHandler) for handler in self.logger.handlers
        ):
            self.memory_handler = MemoryLogHandler()
            self.logger.addHandler(self.memory_handler)

        log_dir = os.path.expanduser("~/ScrapGPT/ScrapGPT/logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, "captioncrunch.log")

        if not any(
            isinstance(handler, logging.FileHandler) for handler in self.logger.handlers
        ):
            self.file_handler = logging.FileHandler(log_file_path)
            formatter = logging.Formatter(
                "%(asctime)s:%(levelname)s:%(name)s: %(message)s"
            )
            self.file_handler.setFormatter(formatter)
            self.logger.addHandler(self.file_handler)
            
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Check if we are in the "collecting" state and if the message is in the correct channel
        if self.game_state == 'collecting' and message.channel == self.voting_channel:
            # Check if the message is enclosed in quotes and is a valid length
            if message.content.startswith('"') and message.content.endswith('"'):
                caption = message.content[1:-1]  # Remove the quotes
                self.submissions[message.author.id] = caption
                await message.reply(f"{message.author.display_name} submitted a caption!")
                await message.delete()  # Delete the user's message after submission
                
    
    
    @commands.hybrid_group(
        name="captioncrunch", description="Commands related to the Caption Crunch game"
    )
    async def captioncrunch_group(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.captioncrunch_help)
    
    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @captioncrunch_group.command(name="setquery")
    async def set_query(self, ctx, *, query: str):
        """Set the search query for Pexels API. Admin only."""
        await self.config.guild(ctx.guild).query.set(query)
        await ctx.send(f"The search query has been updated to: `{query}`")
    
    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @captioncrunch_group.command(name="setchannel")
    async def set_channel(self, ctx):
        """Set the channel for Caption Crunch game submissions."""
        await self.config.guild(ctx.guild).captioncrunch_channel.set(ctx.channel.id)
        await ctx.send(f"Caption Crunch submissions will be accepted in {ctx.channel.mention} from now on.")
    
    @captioncrunch_group.command(name='help', description='Show the help message for Caption Crunch')
    async def captioncrunch_help(self, ctx):
        embed = discord.Embed(
            title='Caption Crunch Help',
            description='Caption Crunch is a game where you submit captions for an image and vote on the best one!',
            color=discord.Color.purple()
        )
        embed.add_field(
            name='Mod / Admin Commands',
            value=(
                '`captioncrunch setquery <query>` - Set the search query for Pexels API '
                '(Admin or Mod only)\n'
                '`captioncrunch setchannel <channel>` - Set the channel for Caption Crunch submissions\n'
                '`captioncrunch setminlength <int>` - Set the minimum caption length\n'
                '`captioncrunch setmaxlength <int>` - Set the maximum caption length\n'
                '`captioncrunch setsubmissiontimeout <int>` - Set the submission timeout\n'
                '`captioncrunch setvotetimeout <int>` - Set the vote timeout\n'
                '`captioncrunch togglerewards` - Toggle rewards for Caption submissions\n'
                '`captioncrunch rewardrange <min: int> <max: int>` - Set the font size for captions\n'
                '`captioncrunch setfontsize` - Set the font size for captions\n'
                
            ),
            inline=False
        )
        embed.add_field(
            name='User Commands',
            value='`captioncrunch start` - Start a new game\n'
                  '`captioncrunch stats <@member>` - Get player stats for yourself or another user if they are mentioned.\n'
                  '`captioncrunch leaderboard` - Display the Caption Crunch leaderboard\n',
            inline=False
        )
        embed.add_field(
                name="About",
                value="Another discord cog by Slurms Mackenzie/ropeadope62\n", inline=False
            )
        embed.add_field(
                name="Repo",
                value="If you liked this, check out my other cogs! https://github.com/ropeadope62/discordcogs",inline=True
            )
        embed.set_thumbnail(url='https://i.ibb.co/wK3vmNp/caption-crunch.png')
        await ctx.send(embed=embed)
    
    @captioncrunch_group.command(name='start', description='Start a new Caption Crunch game')
    async def start(self, ctx):
        # Prevent multiple games from running simultaneously
        if self.game_state:
            await ctx.send("A game is already in progress.")
            return

        self.game_state = 'collecting'
        self.voting_channel = ctx.channel
        submission_timeout = await self.config.guild(ctx.guild).submission_timeout()

        # Check for image attachment
        image_url = None
        if ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            if attachment.content_type.startswith('image/'):
                image_url = attachment.url
            else:
                await ctx.send("The attached file is not an image.")
                self.reset_gamestate()
                return
        else:
            # No attachment provided, use Pexels API
            query = await self.config.guild(ctx.guild).query()
            image_url = await self.fetch_image(query)
            
        if not image_url:
            await ctx.send("Failed to get an image.")
            self.reset_gamestate()
            return

        # Send the initial submission message
        embed = discord.Embed(
            title="Caption Crunch - Submit Your Captions!",
            description=f'**To Submit a caption**, enter some text surrounded by double quotes. For example "this is a caption".\n\nThere are {submission_timeout} seconds remaining.',
            color=discord.Color.purple()
        )
        embed.set_image(url=image_url)
        embed.set_thumbnail(url='https://i.ibb.co/wK3vmNp/caption-crunch.png')
        submission_message = await ctx.send(embed=embed)

        # Collect submissions
        for remaining in range(submission_timeout, 0, -1):
            await asyncio.sleep(1)
            embed.description = f'**To Submit a caption**, enter some text surrounded by double quotes. For example "this is a caption".\n\nThere are {remaining} seconds remaining.'
            embed.set_thumbnail(url='https://i.ibb.co/wK3vmNp/caption-crunch.png')
            await submission_message.edit(embed=embed)

        # Process submissions
        if not self.submissions:
            await ctx.send("No submissions received.")
            self.reset_gamestate()
            return

        await self.process_submissions(ctx, image_url)
        
    async def fetch_image(self, query=None):
        """Fetch an image from Pexels API based on the query."""
        # Load the Pexels API key from environment variables
        pexels_api_key = os.getenv("PEXELS_API_KEY")
        if not pexels_api_key:
            self.logger.error("Pexels API key is not set.")
            return None

        # If no query is provided fetch it from the guild config or default to "people"
        if not query:
            query = await self.config.guild(self.voting_channel.guild).query() or "people" 

        # Set the total number of pages to query from pexels
        total_pages = 100

        # Get a random page number
        random_page = random.randint(1, total_pages)

        url = f"https://api.pexels.com/v1/search?query={query}&per_page=1&page={random_page}"
        headers = {"Authorization": pexels_api_key}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'photos' in data and data['photos']:
                            # Get the first photo's URL (only 1 result per page)
                            image_url = data['photos'][0]['src']['large']
                            return image_url
                        else:
                            self.logger.error(f"No images found for query: {query}")
                            await self.voting_channel.send(f"No images found for query: {query}")
                            return None
                    else:
                        self.logger.error(f"Failed to fetch image, HTTP status: {response.status}")
                        await self.voting_channel.send(f"Failed to fetch image, HTTP status: {response.status}")
                        return None
            except aiohttp.ClientError as e:
                self.logger.error(f"Error fetching image from Pexels API: {str(e)}")
                await self.voting_channel.send(f"Error fetching image from Pexels API: {str(e)}")
                return None


    async def process_submissions(self, ctx, image_url):
        # Stitch all submissions into one wide image
        stitched_image = await self.stitch_submissions(image_url, self.submissions)

        if stitched_image:
            # Send the stitched image with voting instructions
            embed = discord.Embed(
                title="Caption Crunch - Voting",
                description="Choose which caption you like most!",
                color=discord.Color.purple()
            )
            embed.set_image(url="attachment://stitched_image.png")
            embed.set_thumbnail(url='https://i.ibb.co/wK3vmNp/caption-crunch.png')

            await ctx.send(embed=embed, file=discord.File(fp=stitched_image, filename="stitched_image.png"))
            
            #? GAME FLOW STEP 5: Collect votes
            await self.collect_votes(ctx, len(self.submissions))  # Pass the number of submissions to vote

            
    async def add_caption_to_image(self, image_url, caption):
        # Fetch the image from the URL
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    image = Image.open(BytesIO(image_data))

                    # Set up Pillow
                    draw = ImageDraw.Draw(image)
                    font_path = '/home/slurms/ScrapGPT/scrapgpt_data/cogs/CogManager/cogs/captioncrunch/impact.ttf'

                    # Dynamically calculate font size based on caption length
                    max_font_size = 152
                    min_font_size = 72
                    try:
                        font_size = max(min(max_font_size, int(100 / (len(caption) ** 0.5))), min_font_size)
                    except Exception as e:
                        self.logger.error(f"Error setting font size: {e}")
                        font_size = 72
                    try:
                        font = ImageFont.truetype(font_path, font_size)  # Dynamically set font size
                    except IOError:
                        font = ImageFont.load_default()  # Load default if custom font fails

                    # Set the maximum width for the text (90% of the image width)
                    max_text_width = int(image.width * 0.9)

                    # Wrap the text so it fits within the image width
                    wrapped_text = self.wrap_text(draw, caption, font, max_text_width)

                    # Calculate total height of the wrapped text
                    text_height = sum([draw.textbbox((0, 0), line, font=font)[3] for line in wrapped_text]) + len(wrapped_text) * 10

                    # Center the text horizontally and place it near the bottom
                    y_offset = image.height - text_height - 40  # Adjust the vertical position based on the height of the text

                    for line in wrapped_text:
                        # Calculate text size using textbbox to get the bounding box coordinates
                        text_bbox = draw.textbbox((0, 0), line, font=font)
                        text_width = text_bbox[2] - text_bbox[0]

                        # Center the line horizontally
                        text_position = ((image.width - text_width) / 2, y_offset)

                        # Create a drop shadow by drawing the same text slightly offset (black color)
                        shadow_offset = 3  # Offset for the drop shadow
                        shadow_position = (text_position[0] + shadow_offset, text_position[1] + shadow_offset)
                        draw.text(shadow_position, line, font=font, fill="black")

                        # Draw the main text (white color) on top of the shadow
                        draw.text(text_position, line, font=font, fill="white")

                        # Move to the next line
                        y_offset += text_bbox[3] - text_bbox[1] + 10

                    # Save the image to BytesIO
                    image_bytes = BytesIO()
                    image.save(image_bytes, format='PNG')
                    image_bytes.seek(0)  # Reset pointer to the start of the file

                    return image_bytes
                else:
                    self.logger.error(f"Failed to download image: {response.status}")
                    return None

    def wrap_text(self, draw, text, font, max_width):
        """Helper function to wrap text so it fits within the max width of the image."""
        # Split text into lines that fit within the specified max width
        lines = []
        for line in text.split('\n'):
            words = line.split()
            wrapped_line = ''
            for word in words:
                test_line = wrapped_line + word + ' '
                if draw.textbbox((0, 0), test_line, font=font)[2] <= max_width:
                    wrapped_line = test_line
                else:
                    lines.append(wrapped_line)
                    wrapped_line = word + ' '
            lines.append(wrapped_line.strip())
        return lines
                    
    async def stitch_submissions(self, image_url, submissions):
        images = []
        font_path = '/home/slurms/ScrapGPT/scrapgpt_data/cogs/CogManager/cogs/captioncrunch/impact.ttf'

        # Convert submissions dict to list of tuples (user_id, caption)
        submission_list = list(submissions.items())
        
        # Shuffle the submission list to randomize the order and store the mapping
        random.shuffle(submission_list)
        # Store the shuffled order mapping (index -> user_id) for vote counting
        self.submission_order = [user_id for user_id, _ in submission_list]

        #? GAME FLOW STEP 1: Add captions to each image and store them
        for user_id, caption in submission_list:
            image_with_caption = await self.add_caption_to_image(image_url, caption)
            if image_with_caption:
                images.append(Image.open(BytesIO(image_with_caption.read())))

        #? GAME FLOW STEP 2: Create a wide image to hold all submissions
        if not images:
            return None

        # Assume all images are the same height, calculate the total width for the wide image
        total_width = sum(image.size[0] for image in images)
        max_height = max(image.size[1] for image in images)
        
        # Create a new blank image for stitching
        stitched_image = Image.new('RGB', (total_width, max_height + 50), (255, 255, 255))  # Add extra height for numbering

        #? GAME FLOW STEP 3: Paste each image into the stitched image and number them
        x_offset = 0
        draw = ImageDraw.Draw(stitched_image)

        try:
            font = ImageFont.truetype(font_path, 40)  # Load Impact font for numbering
        except IOError:
            font = ImageFont.load_default()  # Default if Impact not available

        for idx, img in enumerate(images, start=1):
            # Paste the image
            stitched_image.paste(img, (x_offset, 50))  # Start 50px from the top to make space for the number

            # Draw the number above the image
            text = str(idx)
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            # Center the number above the image
            text_position = (x_offset + (img.size[0] - text_width) / 2, 10)
            draw.text(text_position, text, font=font, fill="black")  # Draw the number

            # Update the x_offset to position the next image
            x_offset += img.size[0]

        # Step 4: Save the final stitched image in-memory
        image_bytes = BytesIO()
        stitched_image.save(image_bytes, format='PNG')
        image_bytes.seek(0)  # Reset pointer to start of the file

        return image_bytes

    async def start_voting(self, ctx):
        """Start the voting process."""

        self.game_state = 'voting'
        vote_timeout = await self.config.guild(ctx.guild).vote_timeout()

        # Voting embed
        embed = discord.Embed(
            title="Caption Crunch - Voting",
            description=f"Choose the best caption! {vote_timeout} seconds remaining.",
            color=discord.Color.purple()
        )
        voting_message = await ctx.send(embed=embed)

        for remaining in range(vote_timeout, 0, -1):
            await asyncio.sleep(1)
            embed.description = f"Choose the best caption! {remaining} seconds remaining."
            embed.set_thumbnail(url='https://i.ibb.co/wK3vmNp/caption-crunch.png')
            await voting_message.edit(embed=embed)

        await self.collect_votes(ctx)

    async def collect_votes(self, ctx, num_submissions):
        """Collect votes from users and tally the results."""
        vote_counts = {user_id: 0 for user_id in self.submissions}
        vote_timeout = await self.config.guild(ctx.guild).vote_timeout()
        voters = set()  # Track users who have already voted
        

        # Validate the votes
        def check(message):
            if message.channel != ctx.channel:
                return False
            if not message.content.isdigit():
                return False
            if not (1 <= int(message.content) <= num_submissions):
                return False
            if message.author.id in voters:
                return False
            # Use submission_order to check if user is voting for themselves
            vote_num = int(message.content) - 1
            if self.submission_order[vote_num] == message.author.id:
                # Inform the user that they cannot vote for themselves
                self.bot.loop.create_task(
                    ctx.send(f"{message.author.mention} attempted to vote for themselves, nice try!")
                )
                return False
            return True

        try:
            # Collect votes for the duration of the timeout
            for remaining in range(vote_timeout, 0, -1):
                try:
                    # Wait for a vote message that passes the check
                    vote_message = await self.bot.wait_for('message', timeout=1, check=check)
                    vote = int(vote_message.content)

                    # Use submission_order to map vote number to correct user_id
                    user_id = self.submission_order[vote - 1]

                    # Increment the vote count for the selected submission
                    vote_counts[user_id] += 1

                    # Add the voter to the set of voters
                    voters.add(vote_message.author.id)

                    # Delete the vote message to ensure anonymity
                    await vote_message.delete()

                    # Send a confirmation message in the channel and mention the voter
                    await ctx.send(f"{vote_message.author.mention} has voted!")

                except asyncio.TimeoutError:
                    pass

        except asyncio.TimeoutError:
            pass

        # Check if any votes were cast
        if all(count == 0 for count in vote_counts.values()):
            await ctx.send("No one voted! The game is ending.")
            await self.reset_gamestate()
            return

        # Determine the winner based on the vote counts
        winner_id = max(vote_counts, key=vote_counts.get)
        winner_caption = self.submissions[winner_id]

        # Announce the winner in the channel
        winner = self.bot.get_user(winner_id)
        await ctx.send(f"The winning caption is: **{winner_caption}** by {winner.display_name}!")

        # Handle rewards if enabled
        if await self.config.guild(ctx.guild).rewards():
            min_reward = await self.config.guild(ctx.guild).min_reward()
            max_reward = await self.config.guild(ctx.guild).max_reward()
            reward = random.randint(min_reward, max_reward)
            currency_name = await bank.get_currency_name(ctx.guild)
            
            await bank.deposit_credits(winner, reward)
            await self.update_stats(winner_id, winner_caption, reward, vote_counts[winner_id])
            
            
            await ctx.send(
                f"That caption earned them {reward} {currency_name}!"
            )
        else:
            await ctx.send(f"The winner is {winner.display_name} with: **{winner_caption}**!")

        await self.reset_gamestate()

    async def update_stats(self, winner_id, caption, reward, votes):
        """Update user stats after winning."""
        async with self.config.user(self.bot.get_user(winner_id)).all() as user_data:
            user_data["wins"] += 1
            user_data["winnings"] += reward
            if votes > user_data.get("most_votes", 0):
                user_data["most_voted_caption"] = caption
                user_data["most_votes"] = votes

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @captioncrunch_group.command(name="togglerewards")
    async def toggle_rewards(self, ctx):
        """Toggle rewards for winning captions."""
        rewards_enabled = await self.config.guild(ctx.guild).rewards()
        await self.config.guild(ctx.guild).rewards.set(not rewards_enabled)
        if rewards_enabled:
            await ctx.send("Caption Crunch rewards have been disabled.")
        else:
            await ctx.send("Caption Crunch rewards have been enabled.")

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @captioncrunch_group.command(name="setminlength")
    async def set_minlength(self, ctx, minlength: int):
        """Set the minimum length for captions. Admin only."""
        await self.config.guild(ctx.guild).caption_minlength.set(minlength)
        await ctx.send(f"The minimum caption length has been set to: `{minlength}` characters.")

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @captioncrunch_group.command(name="setmaxlength")
    async def set_maxlength(self, ctx, maxlength: int):
        """Set the maximum length for captions. Admin only."""
        await self.config.guild(ctx.guild).caption_maxlength.set(maxlength)
        await ctx.send(f"The maximum caption length has been set to: `{maxlength}` characters.")

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @captioncrunch_group.command(name="setsubmissiontimeout")
    async def set_submission_timeout(self, ctx, timeout: int):
        """Set the submission timeout in seconds. Admin only."""
        await self.config.guild(ctx.guild).submission_timeout.set(timeout)
        await ctx.send(f"The submission timeout has been set to: `{timeout}` seconds.")

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @captioncrunch_group.command(name="setvotetimeout")
    async def set_vote_timeout(self, ctx, timeout: int):
        """Set the vote timeout in seconds. Admin only."""
        await self.config.guild(ctx.guild).vote_timeout.set(timeout)
        await ctx.send(f"The vote timeout has been set to: `{timeout}` seconds.")

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @captioncrunch_group.command(name="setfontsize")
    async def set_font_size(self, ctx, size: int):
        """Set the font size for captions. Admin only."""
        await self.config.guild(ctx.guild).caption_font_size.set(size)
        await ctx.send(f"The caption font size has been set to: `{size}`.")

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @captioncrunch_group.command(name="settings")
    async def settings(self, ctx):
        """Display the current guild configuration settings."""
        guild_config = await self.config.guild(ctx.guild).all()

        embed = discord.Embed(
            title="Caption Crunch Settings",
            description="Current configuration settings for this guild.",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url='https://i.ibb.co/wK3vmNp/caption-crunch.png')

        for key, value in guild_config.items():
            embed.add_field(name=key.replace('_', ' ').title(), value=str(value), inline=False)

        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @captioncrunch_group.command(name="rewardrange")
    async def set_reward_range(self, ctx, min_reward: int, max_reward: int):
        """Set the reward range for winning captions."""
        if min_reward > max_reward:
            await ctx.send("Invalid reward range. Ensure min_reward is less than max_reward.")
            return
        await self.config.guild(ctx.guild).min_reward.set(min_reward)
        await self.config.guild(ctx.guild).max_reward.set(max_reward)
        await ctx.send(f"Reward range set to {min_reward}-{max_reward}.")

    @captioncrunch_group.command(name="stats")
    async def caption_stats(self, ctx, user: discord.User = None):
        """View Caption Crunch stats for yourself or another user."""
        target_user = user or ctx.author
        user_data = await self.config.user(target_user).all()
        
        embed = discord.Embed(
            title=f"Caption Crunch Stats for {target_user.display_name}",
            color=discord.Color.purple()
        )
        embed.add_field(name="Wins", value=user_data['wins'], inline=True)
        embed.add_field(name="Total Winnings", value=f"{user_data['winnings']:,}", inline=True)
        embed.add_field(name="Most Votes Received", value=user_data['most_votes'], inline=True)
        
        if user_data['most_voted_caption']:
            embed.add_field(
                name="Most Popular Caption", 
                value=f"\"{user_data['most_voted_caption']}\"", 
                inline=False
            )
        
        embed.set_thumbnail(url='https://i.ibb.co/wK3vmNp/caption-crunch.png')
        if target_user.avatar:
            embed.set_author(name=target_user.display_name, icon_url=target_user.avatar.url)
        else:
            embed.set_author(name=target_user.display_name)
            
        await ctx.send(embed=embed)

    @captioncrunch_group.command(name="leaderboard")
    async def caption_leaderboard(self, ctx):
        """Show the Caption Crunch leaderboard."""
        all_users = await self.config.all_users()
        sorted_users = sorted(all_users.items(), key=lambda x: x[1]['wins'], reverse=True)

        embed = discord.Embed(
            title="Caption Crunch Leaderboard",
            color=discord.Color.purple()
        )
        
        for i, (user_id, data) in enumerate(sorted_users[:10], 1):
            user = self.bot.get_user(int(user_id))
            if user:
                embed.add_field(
                    name=f"{i}. {user.display_name}",
                    value=f"Wins: {data['wins']}\nTotal Winnings: {data['winnings']}",
                    inline=False
                )

        embed.set_thumbnail(url='https://i.ibb.co/wK3vmNp/caption-crunch.png')
        await ctx.send(embed=embed)
        
    async def reset_gamestate(self):
        # Reset the game state and clear submissions
        self.game_state = None # Clear the game state
        self.submissions = {} # Clear the submissions dictionary
        self.submission_order = []  # Clear the submission order mapping
