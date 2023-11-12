import dotenv
import asyncio 
import random
import aiofiles
import os
import discord
from discord import Embed, File, app_commands, SelectOption, Member
from discord.ext import commands
from discord.ui import Select, View
from dotenv import load_dotenv
import logging
import json 
import io

# Global variables for the bot - these can be changed with slash commands
#TODO: Write these variables to file so they persist between bot restarts

MIN_MESSAGE_LENGTH = 20
REWARDS = True
SUBSCRIBER_BONUS = 2
GOLD_AWARD = 1
ALLOWED_CHANNEL_IDs = [1171917207375183872, 1172234313400582315]

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



load_dotenv()

# utility function for getting all of the bot commands
bot_commands = [command.name for command in bot.commands]


# Utility functions for retrieving and storing user data in the vault

def load_forgesight_vault():
    try: 
        with open("forgesight_vault.json", "r") as file:
            vault = json.load(file)
    except FileNotFoundError:
        vault = {}
    return vault

def save_forgesight_vault(vault):
    with open("forgesight_vault.json", "w") as file:
        json.dump(vault, file, indent=4)

# Ready the bot, sync the commands 
@bot.event
async def on_ready():
    print(f"{bot} has connected to Discord.")
    logger.info(f"{bot} has connected to Discord.")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {synced} commands")
    except Exception as e:
        print(e)
    
# slash command base / group for forgesight

@bot.tree.command(
    name="forgesight",
    description="Forgesight - Community engagement bot for Tableflip Foundry."
)
async def forgesight_command(ctx):
    pass  # This is just to define the group, no action needed here.

# Define the 'log' subcommand within the 'forgesight' group

@bot.tree.command(name="log", description="Get or clear the Forgesight log file\n Usage: /log <get/clear>")
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
            await Interaction.response.send_message("The log file could not be found.", ephemeral=True)
            logger.info("The log file could not be found.")

    elif action == "clear":
        try:
            # Clearing the file
            open(log_file_path, 'w').close()
            await Interaction.response.send_message(f"The log file has been cleared by {Interaction.user}.", ephemeral=True)
            logger.info(f"The log file has been cleared by {Interaction.user}.")
        except Exception as e:
            await Interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
            logger.error(f"An error occurred while trying to clear the log file: {str(e)}")
    else:
        await Interaction.response.send_message("Invalid action. Use 'get' or 'clear'.", ephemeral=True)
        logger.warning(f"Invalid action entered by {Interaction.user} for /forgesight log command.")
    
@bot.tree.command(name="messagelength", description="Set the message size requirements for earning gold")
async def set_messagelength(Interaction: discord.Interaction, min_message_length: int):
    global MIN_MESSAGE_LENGTH
    MIN_MESSAGE_LENGTH = min_message_length
    await Interaction.response.send_message(f"Minimum message length for Gold reward has been set to {MIN_MESSAGE_LENGTH}.", ephemeral=False)
    await logger.info(f"Minimum message length set to {MIN_MESSAGE_LENGTH} by {Interaction.user}")
    
@bot.tree.command(name="subscriberbonus", description="Set the subscriber bonus applied to Gold rewards.")
async def set_subscriberbonus(Interaction: discord.Interaction, subscriber_bonus: int):
    global SUBSCRIBER_BONUS
    SUBSCRIBER_BONUS = subscriber_bonus
    await Interaction.response.send_message(f"Subscriber bonus for Gold reward has been set to {SUBSCRIBER_BONUS}.", ephemeral=False)
    await logger.info(f"Subscriber bonus set to {SUBSCRIBER_BONUS} by {Interaction.user}")

@bot.tree.command(name="rewards", description="Toggle Gold rewards on or off")
async def toggle_rewards(Interaction: discord.Interaction, toggle: str):
    global REWARDS
    if toggle == "on":
        REWARDS = True
        await Interaction.response.send_message(f"Gold rewards have been turned on.", ephemeral=False)
        await logger.info(f"Gold rewards have been turned on by {Interaction.user}")
    elif toggle == "off":
        REWARDS = False
        await Interaction.response.send_message(f"Gold rewards have been turned off.", ephemeral=False)
        await logger.info(f"Gold rewards have been turned off by {Interaction.user}")
    else:
        await Interaction.response.send_message(f"Invalid option. Use 'on' or 'off'.", ephemeral=True)
        await logger.warning(f"Invalid option entered by {Interaction.user} for /forgesight rewards command.")

# Bring up the command list 

@bot.tree.command(name="commands", description="Show a list of all Forgesight commands\n Usage: /commands")
async def commands_list(Interaction: discord.Interaction):
    embed = Embed(
        title="Forgesight Commands",
        description="Here's a list of available commands:",
        color=0xCF2702,  # Cardinal Red
    )

    # Add a field to embed. embed. add_field name value help inline False
    for command in bot.tree.get_commands():
        embed.add_field(name=command.name, value=command.description, inline=False)

    await Interaction.response.send_message(embed=embed)
    logger.info(f"{Interaction.user} used the retrieved the command list.")
    

@bot.tree.command(name="leaderboard", description="Show the Server Gold leaderboard")
async def get_leaderboard(interaction: discord.Interaction):
    try:
        with open('forgesight_vault.json', 'r') as file:
            data = json.load(file)
        leaderboard_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        embed = Embed(title="Forgesight Vault - Ranking", description="Top users by gold", color=0xCF2702)
        for user_id, gold in leaderboard_data:
            user = await bot.fetch_user(int(user_id))
            embed.add_field(name=user.display_name, value=f"{gold} Gold", inline=False)
        await interaction.response.send_message(embed=embed)
    except FileNotFoundError:
        await interaction.response.send_message("The leaderboard data file could not be found.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
@bot.tree.command(name="balance", description="Check a user's gold balance")
async def check_gold(interaction: discord.Interaction, member: discord.Member):
    try:
        # Load the gold data from the vault
        with open('forgesight_vault.json', 'r') as file:
            data = json.load(file)

        # Retrieve the gold balance for the user argued
        gold_balance = data.get(str(member.id), 0)

        # Embed for gold balance
        embed = discord.Embed(
            title=f"Gold Balance",
            description=f"{member.display_name}'s gold balance",
            color=0xCF2702 
        )
        embed.add_field(name="Gold", value=str(gold_balance))

        await interaction.response.send_message(embed=embed)

    except FileNotFoundError:
        await interaction.response.send_message("The gold data file could not be found.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

# ready the bot and sync the commands with slash commands

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        print(f"Received button click: {interaction.data}")


@bot.event
async def on_message(event):
    # We don't want the bot to reply to itself
    if event.author == bot:
        return
    
    if event.channel.id not in ALLOWED_CHANNEL_IDs:
        print(f'Message not in allowed channel {event.channel.id}')
        return

    # If the message is long enough, award gold
    if len(event.content) >= MIN_MESSAGE_LENGTH:
        user_id = str(event.author.id)
        print(f'Message was length {len(event.content)}: Awarding {GOLD_AWARD} gold to {user_id}')
        # async open the vault
        async with aiofiles.open('forgesight_vault.json', 'r') as file:
            data = await file.read()
            vault = json.loads(data) if data else {}

        vault[user_id] = vault.get(user_id, 0) + GOLD_AWARD
        
        # async Save the updated gold data into the vault 
        async with aiofiles.open('forgesight_vault.json', 'w') as file:
            await file.write(json.dumps(vault, indent=4))
        
        print(f"{event.author.mention} has earned {GOLD_AWARD} gold!")
        


# Make the bot send a message in the current channel - more of a test command than anything else
@bot.tree.command(name="say", description="Make the bot say something\n Usage: /say <thing to say>")
async def say(Interaction: discord.Interaction, thing_to_say: str):
    await Interaction.response.send_message(thing_to_say, ephemeral=False)

# Set how much gold each message is worth
@bot.tree.command(name="gold_reward", description="Set the gold reward per message\n Usage: /gold_reward <number of gold>")
async def gold_reward(Interaction: discord.Interaction, number_of_gold: int):
    global GOLD_AWARD
    GOLD_AWARD = number_of_gold
    await Interaction.response.send_message(f"Gold reward per message set to {GOLD_AWARD}", ephemeral=False)
    await logger.info(f"Gold reward per message set to {GOLD_AWARD} by {Interaction.user}")

# Log Forgesight errors
@bot.event
async def on_error(event, *args, **kwargs):
    with open("forgesight_err.log", "a") as f:
        if event == "on_message":
            f.write(f"Unhandled message: {args[0]}\n")
        else:
            raise

# Run the bot with the discord token
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    bot.run(token)
    

