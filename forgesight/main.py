import datetime 
import dotenv
import asyncio
import aiofiles
import logging
import os
import discord
import time
import aiosqlite
from discord import Embed, File
from discord.ext import commands
from dotenv import load_dotenv
import io
import shutil
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
from database import Forgesight_DB_Manager
import sqlite3
import json
import datetime
import aiosqlite

# Global variables for the bot - these can be changed with slash command

# Set up the bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True

# Define the bot
bot = commands.Bot(command_prefix="/", intents=intents)

# My boilerplate logger setup
logger = logging.getLogger("forgesight_log")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("forgesight.log", encoding="utf-8", mode="a")
print(f"Log file created at: {handler.baseFilename}")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

# I've defined a separate logger for the database, so that it can be configured separately
# However, for now most functins are logging to the main logger

db_logger = logging.getLogger("forgesight_db_log")
db_logger.setLevel(logging.DEBUG)
db_handler = logging.FileHandler("forgesight_db.log", encoding="utf-8", mode="a")
print(f"Database Log file created at: {db_handler.baseFilename}")
db_handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)

# Load our environment variables 
load_dotenv()

# Define the database manager object
db_manager = Forgesight_DB_Manager('forgesight.db', logger)

# Create a variable for bot commands which can be used in the help command
bot_commands = [command.name for command in bot.commands]

#! Helper function to combine logging and executing a query
def log_and_execute(cursor, query):
    logger.info(f"Executing query: {query}")
    cursor.execute(query)
    
#! Helper function to check if a user is a mod or admin, there is a built in decorator for this but I prefer granular control
def is_mod_or_admin():
    async def predicate(ctx):
        mod_role = discord.utils.get(ctx.guild.roles, name="Moderation Team")
        owner_role = discord.utils.get(ctx.guild.roles, name="Owner")
        admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
        return mod_role in ctx.author.roles or admin_role in ctx.author.roles or owner_role in ctx.author.roles

    return commands.check(predicate)

# Calculate the total gold in the bank, that is the balance of all users
async def calculate_total_gold():
    total_gold = 0
    async with aiosqlite.connect('forgesight.db') as _:
        try:
            cursor = await db_manager.execute()
            query = 'SELECT SUM(gold) FROM user_data'
            await db_manager.execute(cursor, query)
            print('SQLite: Calculating total gold')  # Debug print statement
            result = await cursor.fetchone()
            total_gold = result[0] if result[0] is not None else 0
        except Exception as e:
            logger.error(f"Error calculating total gold: {e}")
            print('SQLite: Error calculating total gold')  

    return total_gold

# Similar to he calculate_total_gold function, but this one is used to record total gold and earn rates
async def record_total_gold():
    all_data = await db_manager.load_all_vault_data()  
    if not all_data:
        logger.info("No vault data found.")
        return

    total_gold = sum(vault_data['gold'] for vault_data in all_data)
    logger.info(f"Total gold: {total_gold}")

    current_time = datetime.datetime.now()
    previous_time = current_time - datetime.timedelta(hours=1)
    gold_earned_per_hour = total_gold - sum(user_data['gold'] for user_data in vault_data if user_data['timestamp'] < previous_time)

    users_earned_gold = sum(user_data['gold'] > 0 for user_data in vault_data)

    await db_manager.execute('INSERT INTO gold_stats (timestamp, total_gold, gold_earned_per_hour, users_earned_gold) VALUES (?, ?, ?, ?)', (current_time, total_gold, gold_earned_per_hour, users_earned_gold))
    await db_manager.commit()
    
    async def calculate_total_gold():
        async with aiosqlite.connect('forgesight.db') as db:
            try:
                cursor = await db.execute('SELECT SUM(gold) FROM user_data')
                total_gold = await cursor.fetchone()
            except Exception as e:
                logger.error(f"Error calculating total gold: {e}")
            return total_gold

# Function to update the last post time to be used in streak bonus calculations
async def record_last_post_date(user_id):
    await db_manager.execute('UPDATE user_data SET last_post_date = ? WHERE user_id = ?', (datetime.date.today().isoformat(), user_id))
    await db_manager.commit()

# task to manage the record total gold function
async def record_gold_task(): 
    while True:
        logger.info("Starting gold recording task")
        now = datetime.datetime.now()
        next_run = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        logger.info(f"Next run scheduled for {next_run}")
        wait_time = (next_run - now).total_seconds()
        await asyncio.sleep(wait_time)
        await calculate_total_gold()


#! This is in progress, needs to be finished
#! This function will be used to create an image with the users gold balance
async def modify_image(member, gold_balance):
    image = Image.open('./images/ledger-template.png')
    draw = ImageDraw.Draw(image)
    # Choose a font (replace 'font = ImageFont.load_default()' with the font path)
    font_path = './fonts/firstreign.otf'
    font = ImageFont.truetype(font_path, size=12)
    text = f"{member} \n {gold_balance} Gold"
    position = (50,50)
    text_image = Image.new('RGBA', image.size, (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_image)
    text_draw.text((0, 0), text, font=font, fill=(0, 0, 0))
    angle = 45
    rotated_text_image = text_image.rotate(angle, expand=1)
    image.paste(rotated_text_image, position, rotated_text_image)
    image_output = BytesIO()
    image.save(image_output, format='PNG')
    image_output.seek(0)

    return image_output

# Shows the configuration for the bot
@bot.tree.command(name="show_config", description="Show the current Forgesight configuration.\nUsage: /show_config")
async def show_config(Interaction: discord.Interaction):
    guild_id = Interaction.guild_id
    if guild_id is None:
        await Interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    try:
        config = await db_manager.load_config(guild_id)
        if not config:
            logger.warning(f"No configuration found for guild {guild_id}")
            await Interaction.response.send_message("No configuration found for this server.", ephemeral=True)
            return

        embed = discord.Embed(title="Forgesight Configuration", description="Current Configuration Values", color=0xCF2702)
        for key, value in config.items():
            embed.add_field(name=key, value=value or 'Not set', inline=False)
        await Interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        logger.error(f"Error retrieving configuration for guild {guild_id}: {e}")
        await Interaction.response.send_message(
            f"An error occurred while retrieving the configuration: {str(e)}", ephemeral=True
        )

#discord Synchronize the bot tree commands for slash commands
@bot.tree.command(name="sync", description="Sync the bot tree commands. \n Usage: /sync")
async def sync(Interaction: discord.Interaction):
    await Interaction.response.defer()
    logger.info("Syncing bot tree commands")
    print("Syncing bot tree commands")
    synced = await bot.tree.sync()
    await Interaction.followup.send(f"{len(synced)} Bot tree commands synchronized.")
    print(f'{len(synced)} Bot tree commands synchronized.')

#Retrieve the users gold balance - does not take arguments
@bot.tree.command(name="balance", description="Check your gold balance. \n Usage: /balance")
async def balance(Interaction: discord.Interaction):
    member = Interaction.user
    user_name = member.display_name# Set the member to the user who triggered the command
    user_data = await db_manager.load_vault_data(member.id, user_name)  # Fetch user data from the database
   
    if user_data:
        gold_balance = user_data['gold']  # Adjust the index based on your table structure
        image = await modify_image(member, gold_balance)
        embed = discord.Embed(title="Gold Balance", description=f"Gold balance for {member}: {gold_balance}", color=discord.Color.gold())
        embed.set_image(url="attachment://balance.png")
        await Interaction.response.send_message(file=discord.File(image, filename='balance.png'), embed=embed)
    else:
        await Interaction.response.send_message("No data found for the user.", ephemeral=True)

#Manual Backup of the database to a flat file
@bot.tree.command(name="backup", description="Manually Backup the Forgesight database. \n Usage: /backup <filename>")
async def backup_db(Interaction: discord.Interaction, filename: str):
    try:
        shutil.copy('forgesight.db', f'./{filename}.db')
        await Interaction.response.send_message(f"Database backup created at {filename}.db", ephemeral=True)
        logger.info(f"Database backup created at {filename}.db")
    except Exception as e:
        await Interaction.response.send_message(f"Error creating database backup: {e}", ephemeral=True)
        logger.error(f"Error creating database backup: {e}")

#! This is in progress, needs to be finished
#! This will post information about the bot, but should be converted into a commands group so that I can properly implement subcommands 
@bot.tree.command(
    name="forgesight",
    description="Forgesight - Community engagement bot for Tableflip Foundry.")
async def forgesight(Interaction: discord.Interaction):
    embed = discord.Embed(title="Forgesight", description="Forgesight is a TableFlip Foundry Bot, designed to promote engagement and reward participation in our community by our amazing members. Its like having a digital facilitator that rewards your participation and makes our server more fun and interactive!", color=discord.Color.blue())
    embed.add_field(name="Key Features:", value="")
    embed.add_field(name="Gold Rewards - ", value="Earn gold for active participation in discussions. The more you contribute, the more you earn!", inline=False)
    embed.add_field(name="Streak Bonuses - ", value="Earn bonus gold if you interact with others on a regular basis. The longer your streak the larger the bonus!", inline=False)
    embed.add_field(name="Subscriber Perks - ", value="Special bonuses for subscribers, making your contributions even more rewarding.", inline=False)
    embed.add_field(name="Guild Bank - ", value="Store your gold in the guild bank, and use it to purchase items from the shop!", inline=False)
    embed.add_field(name="Leaderboard - ", value="See how you stack up against others in our community with the gold leaderboard!", inline=False)
    file = discord.File("./images/forgesight.png", filename="forgesight.png")
    embed.set_image(url="attachment://forgesight.png")
    await Interaction.response.send_message(file=file, embed=embed)


# Define the 'log' subcommand within the 'forgesight' group

#! This is in progress, needs to be finished
#! This will post the gold stats for the server
@bot.tree.command(
    name="bank", 
    description="Show the current gold balance and stats of the Forgesight Bank.")
async def get_bank(Interaction: discord.Interaction):
    embed = discord.Embed(title="TableFlip Foundry Bank", description="The bank is an important location in the Tableflip Foundry community, where players store their server Gold and items. Gold is earned by actively participating in any of our discussion channels. \n ", color=discord.Color.blue())
    embed.add_field(name="Gold Balance", value=f"The current gold balance of the bank is {await calculate_total_gold()}.", inline=False)
    embed.add_field(name="Reward Rate", value="7 GPH (Gold Per Hour)", inline=False)
    embed.add_field(name="Peak Reward Rate", value="25 GPH", inline=False)
    embed.add_field(name="Average Reward Rate", value="10 GPH", inline=False)
    file = discord.File("./images/bank.png", filename="bank.png")
    embed.set_image(url="attachment://bank.png")
    await Interaction.response.send_message(file=file, embed=embed, ephemeral=False)


#View or clear the log file
@bot.tree.command(
    name="log",
    description="Get or clear the Forgesight log file\n Usage: /log <get/clear>",
)
@is_mod_or_admin()
async def forgesight_log(Interaction: discord.Interaction, action: str = "get"):
    log_file_path = "forgesight.log"  # The path to your log file

    if action == "get":
        try:
            with open(log_file_path, "rb") as log_file:
                log_content = log_file.read()
                log_bytes = io.BytesIO(log_content)
                log_attachment = File(fp=log_bytes, filename="forgesight.log")
                await Interaction.response.send_message(file=log_attachment)
                logger.info(f"The log file was retrieved by {Interaction.user}.")
        except FileNotFoundError:
            await Interaction.response.send_message(
                "The log file could not be found.", ephemeral=True
            )
            logger.info("The log file could not be found.")

    elif action == "clear":
        try:
            # Clearing the file
            open(log_file_path, "w").close()
            await Interaction.response.send_message(
                f"The log file has been cleared by {Interaction.user}.", ephemeral=True
            )
            logger.info(f"The log file has been cleared by {Interaction.user}.")
        except Exception as e:
            await Interaction.response.send_message(
                f"An error occurred: {str(e)}", ephemeral=True
            )
            logger.error(
                f"An error occurred while trying to clear the log file: {str(e)}"
            )
    else:
        await Interaction.response.send_message(
            "Invalid action. Use 'get' or 'clear'.", ephemeral=True
        )
        logger.warning(
            f"Invalid action entered by {Interaction.user} for /forgesight log command."
        )


@bot.tree.command(
    name="set_min_message_length",
    description="Set the minimum message length requirement for earning gold"
)
@is_mod_or_admin()
async def set_min_message_length(Interaction: discord.Interaction, new_length: int):
    if new_length < 0:
        await Interaction.response.send_message("Length must be a positive number.", ephemeral=True)
        return

    guild_id = Interaction.guild_id
    if guild_id is None:
        await Interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    try:
        async with db_manager as db:
            await db.execute("UPDATE config SET min_message_length = ? WHERE guild_id = ?", (new_length, str(guild_id)))
            await db.commit()

        await Interaction.response.send_message(
            f"Minimum message length set to {new_length}.",
            ephemeral=False,
        )
        logger.info(f"Minimum message length set to {new_length} for guild {guild_id}")
    except Exception as e:
        await Interaction.response.send_message(
            f"An error occurred while updating the configuration: {str(e)}", ephemeral=True
        )
        logger.error(f"Error updating configuration: {e}")


@bot.tree.command(
    name="subscriber_bonus",
    description="Set the subscriber bonus applied to Gold rewards.",
)
@is_mod_or_admin()
async def set_subscriberbonus(Interaction: discord.Interaction, subscriber_bonus: int):
    
    if subscriber_bonus < 0:
            await Interaction.response.send_message("Length must be a positive number.", ephemeral=True)
            return

    guild_id = Interaction.guild_id
    if guild_id is None:
        await Interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    try:
        async with db_manager as db:
            await db.execute("UPDATE config SET subscriber_bonus = ? WHERE guild_id = ?", (subscriber_bonus, str(guild_id)))
            await db.commit()

        await Interaction.response.send_message(
            f"Subscriber bonus set to {subscriber_bonus}.",
            ephemeral=False,
        )
        logger.info(f"Subscriber bonus was set to {subscriber_bonus} for guild {guild_id}")
    except Exception as e:
        await Interaction.response.send_message(
            f"An error occurred while updating the configuration: {str(e)}", ephemeral=True
        )
        logger.error(f"Error updating configuration: {e}")


@bot.tree.command(
    name="media_bonus", description="Set the media bonus applied to Gold rewards."
)
@is_mod_or_admin()
async def set_mediabonus(Interaction: discord.Interaction, media_bonus: int):
    
    if media_bonus < 0:
            await Interaction.response.send_message("Bonus must be a positive number.", ephemeral=True)
            return

    guild_id = Interaction.guild_id
    if guild_id is None:
        await Interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    try:
        async with db_manager as db:
            await db.execute("UPDATE config SET media_bonus = ? WHERE guild_id = ?", (media_bonus, str(guild_id)))
            await db.commit()

        await Interaction.response.send_message(
            f"Media bonus set to {media_bonus}.",
            ephemeral=False,
        )
        logger.info(f"Subscriber bonus was set to {media_bonus} for guild {guild_id}")
    except Exception as e:
        await Interaction.response.send_message(
            f"An error occurred while updating the configuration: {str(e)}", ephemeral=True
        )
        logger.error(f"Error updating configuration: {e}")

#! get_mediabonus is for debug/testing purposes only, can be removed later

@bot.tree.command(
    name="get_mediabonus",
    description="Get the current media bonus applied to Gold rewards."
)
@is_mod_or_admin()
async def get_mediabonus(Interaction: discord.Interaction):
    guild_id = Interaction.guild_id
    config_vals = await db_manager.load_config(guild_id)
    media_bonus = config_vals.get('media_bonus', 0)
    await Interaction.response.send_message(
        f"The current media bonus for Gold rewards is {media_bonus}.", ephemeral=False
    )


@bot.tree.command(name="toggle_rewards", description="Toggle Gold rewards on or off. \n Usage: /toggle_rewards <on/off>")
@is_mod_or_admin()
async def toggle_rewards(Interaction: discord.Interaction, toggle: str):
    guild_id = Interaction.guild_id
    if guild_id is None: 
        await Interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    try: 
        async with db_manager as db:
            await db.execute("UPDATE config SET rewards_enabled = ? WHERE guild_id = ?", (1 if toggle == "on" else 0, str(guild_id)))
            await db.commit()
        await Interaction.response.send_message(
            "Gold rewards have been turned on." if toggle == "on" else "Gold rewards have been turned off.", ephemeral=False
        )
        logger.info(f"Gold rewards have been turned {'on' if toggle == 'on' else 'off'} by {Interaction.user}")
    except Exception as e:
        await Interaction.response.send_message(
            f"An error occurred while updating the configuration: {str(e)}", ephemeral=True
        )
        logger.error(f"Error updating configuration: {e}")


@bot.tree.command(
    name="reward_timeout",
    description="Set the timeout for Gold rewards in seconds between messages.",
)
@is_mod_or_admin()
async def set_reward_timeout(Interaction: discord.Interaction, timeout: int):
    guild_id = Interaction.guild_id
    if guild_id is None:
        await Interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    if timeout < 0:
        await Interaction.response.send_message(
            f"Invalid timeout: {timeout}. Timeout must be a positive integer.",
            ephemeral=True,
        )
        logger.warning(
            f"Invalid timeout entered by {Interaction.user} for /reward_timeout command."
        )
        return
    try: 
        async with db_manager as db: 
            await db.execute("UPDATE config SET reward_timeout = ? WHERE guild_id = ?", (timeout, str(guild_id)))
            await db.commit()
        await Interaction.response.send_message(f"Reward timeout set to {timeout} seconds.", ephemeral=False)
        logger.info(f"Message reward timeout set to {timeout} seconds by {Interaction.user}")
    except Exception as e:
        await Interaction.response.send_message(
            f"An error occurred while updating the configuration: {str(e)}", ephemeral=True
        )
        logger.error(f"Error updating configuration: {e}")
        

@bot.tree.command(
    name="channel_restriction",
    description="Toggle channel restriction on or off. \n Usage: /toggle_channel_restriction <on/off>",
)
@is_mod_or_admin()
async def toggle_channel_id_restriction(Interaction: discord.Interaction, toggle: str):
    guild_id = Interaction.guild_id
    if guild_id is None: 
        await Interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    try: 
        async with db_manager as db:
            await db.execute("UPDATE config SET channel_id_restriction = ? WHERE guild_id = ?", (1 if toggle == "on" else 0, str(guild_id)))
            await db.commit()
            await Interaction.response.send_message(
                    "Channel Restrictions have been enabled." if toggle == "on" else "Channel Restrictions have been disabled.", ephemeral=False
                )
            logger.info(f"Gold rewards have been turned {'on' if toggle == 'on' else 'off'} by {Interaction.user}")
    except Exception as e:
        await Interaction.response.send_message(f"An error occurred while updating the configuration: {str(e)}", ephemeral=True)
        
    
@bot.tree.command(
    name="toggle_min_message_requirement",
    description="Toggle the message reward timeout on or off. \n Usage: /toggle_reward_timeout <on/off>",
)
@is_mod_or_admin()
async def toggle_min_message_requirement(Interaction: discord.Interaction, toggle: str):
    guild_id = Interaction.guild_id
    if guild_id is None: 
        await Interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    try: 
        async with db_manager as db:
            await db.execute("UPDATE config SET  min_message_requirement = ? WHERE guild_id = ?", (1 if toggle == "on" else 0, str(guild_id)))
            await db.commit()
            await Interaction.response.send_message(
                    "Message Length Requirements have been enabled." if toggle == "on" else "Message Length Requirements have been disabled.", ephemeral=False
                )
            logger.info(f"Message Length Requirements have been turned {'on' if toggle == 'on' else 'off'} by {Interaction.user}")
    except Exception as e:
        await Interaction.response.send_message(f"An error occurred while updating the configuration: {str(e)}", ephemeral=True)

@bot.tree.command(
    name = "set_streak_bonus", 
    description = "Set the streak bonus applied to Gold rewards."
)
@is_mod_or_admin() 
async def set_streak_bonus (Interaction: discord.Interaction, streak_bonus: int):
    guild_id = Interaction.guild_id
    if guild_id is None: 
        await Interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    try: 
        async with db_manager as db: 
            await db.execute('UPDATE config SET streak_bonus = ? WHERE guild_id = ?', (streak_bonus, str(guild_id)))
            await db.commit()
            await Interaction.response.send_message(f"Streak bonus set to {streak_bonus}.", ephemeral=False)
            logger.info(f"Streak bonus was set to {streak_bonus} for guild {guild_id}")
    except Exception as e:
        await Interaction.response.send_message(f"An error occurred while updating the configuration: {str(e)}", ephemeral=True)
        logger.error(f"Error updating configuration: {e}")
    
@bot.tree.command(
    name="get_user_data",
    description="Get the Forgesight user data for a specific user. \n Usage: /get_user_data <user_id>"
)
@is_mod_or_admin()
async def get_user_data(Interaction: discord.Interaction, member: discord.Member):
    user_id = str(member.id)
    user_data = await db_manager.load_vault_data_from_id(user_id)
    if user_data:
        embed = discord.Embed(title="Forgesight User Data", description="Current User Data", color=0xCF2702)
        for key, value in user_data.items():
            embed.add_field(name=key, value=value or 'Not set', inline=False)
        await Interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await Interaction.response.send_message("No data found for the user.", ephemeral=True)
        
@bot.tree.command(
    name="commands",
    description="Show a list of all Forgesight commands\n Usage: /commands",
)
async def commands_list(Interaction: discord.Interaction):
    embed = Embed(
        title="Forgesight Commands",
        description="Here's a list of available commands:",
        color=0xCF2702,  # Cardinal Red
    )
    for command in bot.tree.get_commands():
        embed.add_field(name=command.name, value=command.description, inline=False)

    await Interaction.response.send_message(embed=embed)
    print(
        f"{Interaction.user} used the retrieved the command list."
    )  #! Debug print statement
    logger.info(f"{Interaction.user} used the retrieved the command list.")



@bot.tree.command(
    name="gold_leaderboard",
    description="Show the Server Gold leaderboard. \n Usage: /gold_leaderboard",
)
async def get_leaderboard(interaction: discord.Interaction):
    try:
        # Connect to the database
        with sqlite3.connect("forgesight.db") as conn:
            cursor = conn.cursor()
            try:
                # Execute the query to get the top 10 users by gold
                cursor.execute("SELECT user_id, gold FROM user_data ORDER BY gold DESC LIMIT 10")
                leaderboard_data = cursor.fetchall()
            except Exception as e:
                logger.error(f"Error retrieving leaderboard data: {e}")
                await interaction.response.send_message(
                    f"An error occurred while retrieving the leaderboard: {str(e)}", ephemeral=True
                )
                return

        embed = Embed(
            title="Forgesight Vault - Ranking",
            description="Top users by gold",
            color=0xCF2702,
        )
        for user_id, gold in leaderboard_data:
            user = await bot.fetch_user(int(user_id))
            embed.add_field(name=user.display_name, value=f"{gold} Gold", inline=False)

        await interaction.response.send_message(embed=embed)
        print(f"{interaction.user} retrieved the Gold leaderboard.")  # Debug print statement
        logger.info(f"{interaction.user} retrieved the Gold leaderboard.")

    except sqlite3.Error as e:
        await interaction.response.send_message(
            f"An error occurred while retrieving the leaderboard: {str(e)}", ephemeral=True
        )
        logger.error(f"An error occurred while retrieving the leaderboard: {str(e)}")

# Needs revising
@bot.tree.command(name="goldbalance", description="Show your gold balance.")
async def gold_balance_command(Interaction: discord.Interaction, member: discord.Member):
    await Interaction.response.defer()
    user_id = str(member.id)
    user_data = await db_manager.load_vault_data(user_id)
    if user_data:
        gold_balance = user_data[1]  # Assuming 'gold' is the second column in user_data
        await Interaction.followup.send(f"{member.display_name} has {gold_balance} gold.")
    else:
        await Interaction.followup.send(f"No data found for {member.display_name}.")


def calculate_streak_bonus(user_data):
    print(f'calculating streak bonus for {user_data[2]}')

#monitor messages for gold rewards
@bot.event
async def on_message(event):
    if not event.guild:  # Ignore DMs or check for guild existence
        return

    guild_id = event.guild.id
    user_id = str(event.author.id)
    user_name = str(event.author.display_name)

    try:
        config_vals = await db_manager.load_config(guild_id)
        if not config_vals:
            logger.warning(f"No configuration found for guild {guild_id}")
            return

        user_data = await db_manager.load_vault_data(user_id, user_name)
        if not user_data:
            logger.warning(f"No user data found for user {user_id}")
            return

        # Check channel restrictions
        if config_vals['channel_id_restriction'] == 1 and event.channel.id not in config_vals['allowed_channels']:
            logger.debug(f"Message in channel {event.channel.id} is not allowed for rewards.")
            return

        # Check message length requirement
        if config_vals['min_message_requirement'] == 1 and len(event.content) < config_vals['min_message_length']:
            logger.debug("Message was not long enough for rewards")
            return

        # Check reward timeout
        last_earned_timestamp = float(user_data.get('last_earned', 0))
        if time.time() - last_earned_timestamp < config_vals['reward_timeout']:
            logger.info(f"{event.author} has already earned gold recently.")
            return

        # Calculate gold award
        current_gold_award = config_vals['base_gold']
        if any(role.id == config_vals.get('subscriber_role_id') for role in event.author.roles):
            current_gold_award += int(config_vals.get('subscriber_bonus', 0))

        if event.attachments:
            current_gold_award += int(config_vals.get('media_bonus', 0))
            user_data['media_bonuses'] = int(user_data.get('media_bonuses', 0)) + 1

        # Update user data
        user_data['gold'] = int(user_data.get('gold', 0)) + current_gold_award
        user_data['last_earned'] = time.time()
        user_data['total_msg_count'] = int(user_data.get('total_msg_count', 0)) + 1
        user_data['msg_avg_length'] = int(user_data.get('msg_avg_length', 0)) + len(event.content)
        user_data['last_post_date'] = datetime.date.today().isoformat()

        # Save the updated user data
        await db_manager.save_vault_data(**user_data)
        logger.info('Forgesight Reward Recorded: ' + str(user_data))

    except Exception as e:
        logger.error(f"Error in on_message: {e}")
        
# Grant gold to a user        
@bot.tree.command(name="grant_gold", description="Grant gold to a user\n Usage: /grant_gold <@user> <amount of gold>")
@is_mod_or_admin()
async def grant_gold(Interaction: discord.Interaction, user: discord.Member, amount: int):
    await Interaction.response.defer()
    user_id = str(user.id)
    user_name = user.display_name
    user_data = await db_manager.load_vault_data(user_id, user_name)
    
    if user_data:
        new_gold = user_data['gold'] + amount 
        logger.info(f"Granted {amount} gold to {user}. New gold: {new_gold}")

        user_data['gold'] = new_gold

        await db_manager.save_vault_data(**user_data) 
        await Interaction.followup.send(f"{amount} gold granted to {user.mention}.", ephemeral=False)
    else:
        await db_manager.create_new_user(user_id, user_name, gold=amount)
        await Interaction.followup.send(f"No data found for {user.mention}. User entry was created for {user.mention} and {amount} has been added to their account.", ephemeral=True)

@bot.tree.command(name="deduct_gold", description="Deduct gold to a user\n Usage: /deduct_gold <@user> <amount of gold>")
@is_mod_or_admin()
async def deduct_gold(Interaction: discord.Interaction, user: discord.Member, amount: int):
    await Interaction.response.defer()
    user_id = str(user.id)
    user_name = user.display_name
    user_data = await db_manager.load_vault_data(user_id, user_name)

    if user_data:
        new_gold = user_data['gold'] - amount
        user_data['gold'] = new_gold
        logger.info(f"Deducted {amount} gold from {user}. New gold: {new_gold}")
        await db_manager.save_vault_data(**user_data)  
        await Interaction.followup.send(f"{amount} gold deducted {user.mention}.", ephemeral=False)
    else:
        await Interaction.followup.send(f"No data found for {user.mention}.", ephemeral=True)

@bot.tree.command(
    name="send_db",
    description="Send the Forgesight database file to a user",
)
@is_mod_or_admin()
async def send_db(Interaction: discord.Interaction, user: discord.User):
    try:
        with open("forgesight.db", "rb") as file:
            await user.send(file=discord.File(file, "forgesight.db"))
        await Interaction.response.send_message(
            f"The Forgesight database file has been sent to {user.mention}",
            ephemeral=False
        )
    except Exception as e:
        await Interaction.response.send_message(
            f"Failed to send the Forgesight database file: {str(e)}",
            ephemeral=True
        )


# Make the bot send a message in the current channel - more of a test command than anything else
@bot.tree.command(
    name="say", description="Make the bot say something\n Usage: /say <thing to say>"
)
@is_mod_or_admin()
async def say(Interaction: discord.Interaction, thing_to_say: str):
    await Interaction.response.send_message(thing_to_say, ephemeral=False)


# Set how much gold each message is worth
@bot.tree.command(
    name="default_gold_award",
    description="Set the gold reward per message.\n Usage: /gold_reward <number of gold>",
)
@is_mod_or_admin()
async def gold_reward(Interaction: discord.Interaction, number_of_gold: int):
    await db_manager.update_config_value("base_gold", number_of_gold)
    await Interaction.response.send_message(
        f"Gold reward per message set to {number_of_gold}", ephemeral=False
    )
    logger.info(f"Gold reward per message set to {number_of_gold} by {Interaction.user}")


@bot.event
async def on_error(event_name, *args, **kwargs):
    with open('error_log.txt', 'a', encoding='utf-8') as f:
        f.write(f"Unhandled message: {args[0]}\n")

# Do some stuff when the bot logs in
@bot.event
async def on_ready():
    db_manager = Forgesight_DB_Manager('forgesight.db', logger)
    await db_manager.initialize_db()
    print('Database initialized')
    logger.info(f"{bot} has connected to Discord.")
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Bot ID: {bot.user.id}")
    print(f"Bot has loaded extensions: {bot.extensions}")
    print("------")
    logger.info(f"Logged in as {bot.user.name} Discord.py API version: {discord.__version__} Bot ID: {bot.user.id}")
    print(f"{bot} has connected to Discord.")
    logger.info(f"{bot} has connected to Discord.")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {synced} commands")
    except Exception as e:
        print(e)

# Run the bot with the discord token
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    bot.run(token)
