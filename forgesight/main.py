import datetime 
import dotenv
import asyncio
import aiofiles
import logging
import os
import discord
import time
from discord import Embed, File
from discord.ext import commands
from dotenv import load_dotenv
import json
import io
import asyncio
import shutil

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

# Load the .env file
load_dotenv()


# utility function for getting all of the bot commands
bot_commands = [command.name for command in bot.commands]

def save_config_vals(variables, file_path):
    with open(file_path, 'w') as file:
        json.dump(variables, file)
        
config_vals = {'MIN_MESSAGE_REQUIRED': True, 'MIN_MESSAGE_LENGTH': 20, 'REWARDS': True,
               'MESSAGE_REWARD_TIMEOUT': 10, 'SUBSCRIBER_ROLE_ID': 1074071214022201378,
               'SUBSCRIBER_BONUS': 2, 'MEDIA_BONUS': 2, 'GOLD_AWARD': 1, 'CHANNEL_ID_RESTRICTION': False,
                'ALLOWED_CHANNEL_IDs': [1171917207375183872, 1172234313400582315], 'OMIT_REWARDS_IDs': [1012659859516297217]}

save_config_vals(config_vals, 'forgesight_config.json')



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


# Utility function for checking if a user is a mod or admin
def is_mod_or_admin():
    async def predicate(ctx):
        mod_role = discord.utils.get(ctx.guild.roles, name="Moderation Team")
        owner_role = discord.utils.get(ctx.guild.roles, name="Owner")
        admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
        return mod_role in ctx.author.roles or admin_role in ctx.author.roles or owner_role in ctx.author.roles

    return commands.check(predicate)

@bot.command()
async def bank(ctx):
    embed = discord.Embed(title="TableFlip Foundry Bank", description="The bank is an important location in the Tableflip Foundry community, where players store their server Gold and items. Gold is earned by actively participating in any discussion happening on ", color=discord.Color.blue())
    file = discord.File("./images/bank.png", filename="bank.png")
    embed.set_image(url="attachment://bank.png")
    await ctx.send(file=file, embed=embed)


async def backup_vault(source, backup_dir, interval_seconds):
    while True:
        shutil.copy(source, backup_dir)
        time.sleep(interval_seconds)
        
        await backup_vault('forgesight_vault.json', './forgesight_vault_backup.json', 3600)

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
    description="Forgesight - Community engagement bot for Tableflip Foundry.")
async def forgesight(Interaction: discord.Interaction):
    embed = discord.Embed(title="Forgesight", description="Forgesight is a TableFlip Foundry Bot, designed to promote engagement and reward participation in our community by our amazing members. Its like having a digital facilitator that rewards your participation and makes our server more fun and interactive!", color=discord.Color.blue())
    embed.add_field(name="Key Features:", value="")
    embed.add_field(name="Gold Rewards - ", value="Earn gold for active participation in discussions. The more you contribute, the more you earn!", inline=False)
    embed.add_field(name="Subscriber Perks - ", value="Special bonuses for subscribers, making your contributions even more rewarding.", inline=False)
    embed.add_field(name="Guild Bank - ", value="Store your gold in the guild bank, and use it to purchase items from the shop!", inline=False)
    embed.add_field(name="Leaderboard - ", value="See how you stack up against others in our community with the gold leaderboard!", inline=False)
    file = discord.File("./images/forgesight.png", filename="forgesight.png")
    embed.set_image(url="attachment://forgesight.png")
    await Interaction.response.send_message(file=file, embed=embed)


# Define the 'log' subcommand within the 'forgesight' group


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
    name="message_length",
    description="Set the message size requirements for earning gold",
)
@is_mod_or_admin()
async def set_messagelength(Interaction: discord.Interaction, min_message_length: int):
    config_vals['MIN_MESSAGE_LENGTH'] = min_message_length
    await Interaction.response.send_message(
        f"Minimum message length for Gold reward has been set to {config_vals['MIN_MESSAGE_LENGTH']}.",
        ephemeral=False,
    )
    logger.info(
        f"Minimum message length set to {config_vals['MIN_MESSAGE_LENGTH']} by {Interaction.user}"
    )


@bot.tree.command(
    name="subscriber_bonus",
    description="Set the subscriber bonus applied to Gold rewards.",
)
@is_mod_or_admin()
async def set_subscriberbonus(Interaction: discord.Interaction, subscriber_bonus: int):
    if subscriber_bonus < 0:
        await Interaction.response.send_message(
            f"Invalid subscriber bonus: {subscriber_bonus}. Subscriber bonus must be a positive integer.",
            ephemeral=True,
        )
        logger.warning(
            f"Invalid subscriber bonus entered by {Interaction.user} for /forgesight subscriberbonus command."
        )
        return
    config_vals['SUBSCRIBER_BONUS'] = subscriber_bonus
    await Interaction.response.send_message(
        f"Subscriber bonus for Gold reward has been set to {config_vals['SUBSCRIBER_BONUS']}.",
        ephemeral=False,
    )
    logger.info(f"Subscriber bonus set to {config_vals['SUBSCRIBER_BONUS']} by {Interaction.user}")


@bot.tree.command(
    name="media_bonus", description="Set the media bonus applied to Gold rewards."
)
@is_mod_or_admin()
async def set_mediabonus(Interaction: discord.Interaction, media_bonus: int):
    if media_bonus < 0:
        await Interaction.response.send_message(
            f"Invalid media bonus: {media_bonus}. Media bonus must be a positive integer.",
            ephemeral=True,
        )
        logger.warning(
            f"Invalid media bonus entered by {Interaction.user} for /forgesight media_bonus command."
        )
        return
    config_vals['MEDIA_BONUS'] = media_bonus
    await Interaction.response.send_message(
        f"Media bonus for Gold reward has been set to {config_vals['SUBSCRIBER_BONUS']}.",
        ephemeral=False,
    )
    logger.info(f"Media bonus set to {config_vals['SUBSCRIBER_BONUS']} by {Interaction.user}")


@bot.tree.command(
    name="toggle_rewards",
    description="Toggle Gold rewards on or off. \n Usage: /toggle_rewards <on/off>",
)
@is_mod_or_admin()
async def toggle_rewards(Interaction: discord.Interaction, toggle: str):
    if toggle == "off":
        config_vals['REWARDS'] = False
        await Interaction.response.send_message(
            "Gold rewards have been turned off.", ephemeral=False
        )
        logger.info(f"Gold rewards have been turned off by {Interaction.user}")
    elif toggle == "on":
        config_vals['REWARDS'] = True
        await Interaction.response.send_message(
            "Gold rewards have been turned on.", ephemeral=False
        )
        logger.info(f"Gold rewards have been turned on by {Interaction.user}")
    else:
        await Interaction.response.send_message(
            "Invalid option. Use 'on' or 'off'.", ephemeral=True
        )
        logger.warning(
            f"Invalid option entered by {Interaction.user} for /forgesight rewards command."
        )


@bot.tree.command(
    name="reward_timeout",
    description="Set the timeout for Gold rewards in seconds between messages.",
)
@is_mod_or_admin()
async def set_reward_timeout(Interaction: discord.Interaction, timeout: int):
    if timeout < 0:
        await Interaction.response.send_message(
            f"Invalid timeout: {timeout}. Timeout must be a positive integer.",
            ephemeral=True,
        )
        logger.warning(
            f"Invalid timeout entered by {Interaction.user} for /forgesight reward_timeout command."
        )
        return
    config_vals['MESSAGE_REWARD_TIMEOUT'] = timeout
    await Interaction.response.send_message(
        f"Message reward timeout set to {config_vals['MESSAGE_REWARD_TIMEOUT']} seconds.",
        ephemeral=False,
    )
    logger.info(
        f"Message reward timeout set to {config_vals['MESSAGE_REWARD_TIMEOUT']} by {Interaction.user}"
    )

@bot.tree.command(
    name="channel_restriction",
    description="Toggle channel restriction on or off. \n Usage: /toggle_channel_restriction <on/off>",
)
@is_mod_or_admin()
async def toggle_channel_restriction(Interaction: discord.Interaction, toggle: str):
    global CHANNEL_ID_RESTRICTION
    if toggle == "off":
        CHANNEL_ID_RESTRICTION = None
        await Interaction.response.send_message(
            "Channel restriction has been turned off.", ephemeral=False
        )
        logger.info(f"Channel restriction has been turned off by {Interaction.user}")
    elif toggle == "on":
        CHANNEL_ID_RESTRICTION = Interaction.channel.id
        await Interaction.response.send_message(
            f"Channel restriction has been turned on for channel {Interaction.channel.mention}.", ephemeral=False
        )
        logger.info(f"Channel restriction has been turned on for channel {Interaction.channel.mention} by {Interaction.user}")
    else:
        await Interaction.response.send_message(
            "Invalid option. Use 'on' or 'off'.", ephemeral=True
        )
        logger.warning(
            f"Invalid option entered by {Interaction.user} for /forgesight toggle_channel_restriction command."
        )

@bot.tree.command(
    name="toggle_reward_timeout",
    description="Toggle the message reward timeout on or off. \n Usage: /toggle_reward_timeout <on/off>",
)
@is_mod_or_admin()
async def toggle_reward_timeout(Interaction: discord.Interaction, toggle: str):
    if toggle == "off":
        config_vals['MESSAGE_REWARD_TIMEOUT'] = None
        await Interaction.response.send_message(
            "Message reward timeout has been turned off.", ephemeral=False
        )
        logger.info(f"Message reward timeout has been turned off by {Interaction.user}")
    elif toggle == "on":
        await Interaction.response.send_message(
            "Enter the timeout in seconds:", ephemeral=True
        )
        def check(m):
            return m.author == Interaction.user and m.channel == Interaction.channel and m.content.isdigit()
        try:
            msg = await bot.wait_for('message', check=check, timeout=30.0)
            config_vals['MESSAGE_REWARD_TIMEOUT'] = int(msg.content)
            await Interaction.response.send_message(
                f"Message reward timeout set to {MESSAGE_REWARD_TIMEOUT} seconds.",
                ephemeral=False,
            )
            logger.info(
                f"Message reward timeout set to {MESSAGE_REWARD_TIMEOUT} by {Interaction.user}"
            )
        except asyncio.TimeoutError:
            await Interaction.response.send_message(
                "Timeout. Please try again.", ephemeral=True
            )
    else:
        await Interaction.response.send_message(
            "Invalid option. Use 'on' or 'off'.", ephemeral=True
        )
        logger.warning(
            f"Invalid option entered by {Interaction.user} for /forgesight toggle_reward_timeout command."
        )



# Bring up the command list


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

    # Add a field to embed. embed. add_field name value help inline False
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
        with open("forgesight_vault.json", "r") as file:
            data = json.load(file)
        leaderboard_data = sorted(
            data.items(), key=lambda x: x[1]["gold"], reverse=True
        )[:10]  # limit to first 10 items
        embed = Embed(
            title="Forgesight Vault - Ranking",
            description="Top users by gold",
            color=0xCF2702,
        )
        for user_id, user_data in leaderboard_data:
            user = await bot.fetch_user(int(user_id))
            gold = user_data["gold"]
            embed.add_field(name=user.display_name, value=f"{gold} Gold", inline=False)
        await interaction.response.send_message(embed=embed)
        print(
            f"{interaction.user} retrieved the Gold leaderboard."
        )  #! Debug print statement
        logger.info(f"{interaction.user} retrieved the Gold leaderboard.")
    except FileNotFoundError:
        await interaction.response.send_message(
            "The leaderboard data file could not be found.", ephemeral=True
        )
        logger.info(
            "File Not Found Error:The leaderboard data file could not be found."
        )
    except discord.NotFound:
        # Handle the specific NotFound error
        print("Interaction expired or not found")
    except Exception as e:
        await interaction.response.send_message(
            f"An error occurred: {str(e)}", ephemeral=True
        )
        logger.info(f"An error occurred: {str(e)}")


@bot.tree.command(
    name="gold_balance",
    description="Check a user's gold balance. \n Usage: /gold_balance <@user>",
)
async def check_gold(interaction: discord.Interaction, member: discord.Member):
    try:
        # Load the gold data from the vault
        with open("forgesight_vault.json", "r") as file:
            data = json.load(file)

        # Retrieve the gold balance for the user argued
        gold_balance = data.get(str(member.id), 0)["gold"]

        # Embed for gold balance
        embed = discord.Embed(
            title="Gold Balance",
            description=f"{member.display_name}'s gold balance",
            color=0xCF2702,
        )
        embed.add_field(name="Gold", value=str(gold_balance))

        await interaction.response.send_message(embed=embed)
        print(
            f"{interaction.user} retrieved {member.display_name}'s gold balance."
        )  #! Debug print statement
        logger.info(
            f"{interaction.user} retrieved {member.display_name}'s gold balance."
        )

    except FileNotFoundError:
        await interaction.response.send_message(
            "The gold data file could not be found.", ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"An error occurred: {str(e)}", ephemeral=True
        )


# ready the bot and sync the commands with slash commands


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        print(f"Received button click: {interaction.data}")

def calculate_streak_bonus(user_data, user_id):
    # Parse the last post date and calculate the difference from today
    today = datetime.date.today()
    last_post_date = datetime.date.fromisoformat(user_data['last_post_date']) if user_data['last_post_date'] else None

    if last_post_date and (today - last_post_date).days == 1:
        # Increment consecutive days, up to a maximum of 5
        user_data['consecutive_days'] = min(user_data['consecutive_days'] + 1, 5)
    else:
        user_data['consecutive_days'] = 1

    # Update the last post date to today
    user_data['last_post_date'] = today.isoformat()

    # Calculate and return the streak bonus
    return user_data['consecutive_days']


@bot.event
async def on_message(event):
    # We don't want the bot to reply to itself
    if event.author == bot:
        return
    if event.author.id == bot.user.id:
        print(f"User is the bot -  {event.author}, skipping rewards")
        logger.info(f"User is the bot -  {event.author}, skipping rewards")
        return
    if event.author.id in config_vals['OMIT_REWARDS_IDs']:
        print('User is in OMIT_REWARDS_IDs, skipping reward')
        logger.info(f'User is in OMIT_REWARDS_IDs, skipping reward')
        return
    # Check that the rewards are enabled 
    if config_vals['REWARDS'] == True:
        vault = load_forgesight_vault()
        # Detarmine if channel id restriction is enabled, if so, check if the message is in an allowed channel
        if config_vals['CHANNEL_ID_RESTRICTION'] and event.channel.id not in config_vals['ALLOWED_CHANNEL_IDs']:
            print(
                f"Message not in allowed channel {event.channel.id}"
            )  #! Debug print statement, do not log this event due to spam
            return
        current_gold_award = config_vals['GOLD_AWARD']
        # Check if message length check is enabled
        if config_vals['MIN_MESSAGE_REQUIRED']:
            # If the message is long enough, award gold
            if len(event.content) >= config_vals['MIN_MESSAGE_LENGTH']:
                # If the user is a subscriber, apply the subscriber bonus
                if any(role.id == config_vals['SUBSCRIBER_ROLE_ID'] for role in event.author.roles):
                    current_gold_award *= config_vals['SUBSCRIBER_BONUS']
                    print(
                        f"User {event.author.mention} has supporter role: Applying supporter bonus, new gold reward is {current_gold_award}"
                    )  #! Debug print statement
                # If the message has attachments, apply the media bonus
                if event.attachments:
                    current_gold_award += config_vals['MEDIA_BONUS']
                    print(
                        f"Message has attachments: Applying media bonus, new gold reward is {current_gold_award}"
                    )  #! Debug print statement
                # Open the vault and retrieve the user's data
                async with aiofiles.open("forgesight_vault.json", "r") as file:
                    data = await file.read()
                    vault = json.loads(data) if data else {}
                user_id = str(event.author.id)
                user_data = vault.get(user_id, {"gold": 0, "last_earned": 0, "consecutive_days": 0, "last_post_date": ""})
                # If the user has earned gold in the past MESSAGE_REWARD_TIMEOUT seconds, don't award gold
                if time.time() - user_data["last_earned"] < config_vals['MESSAGE_REWARD_TIMEOUT']:
                    print(
                        f"{event.author.mention} has already earned gold in the past {config_vals['MESSAGE_REWARD_TIMEOUT']} seconds."
                    )  #! Debug print statement
                    return
                # Award the gold and update the vault with new gold and last earned time
                
                user_data["gold"] += current_gold_award
                print('Awarded base gold')
                streak_bonus = calculate_streak_bonus(user_data, user_id)
                user_data["gold"] += streak_bonus
                print(f"Awarded streak bonus of {streak_bonus} gold")
                user_data["last_earned"] = time.time()
                print(
                    f'Setting last earned time to {user_data["last_earned"]}'
                )  #! Debug print statement
                vault[user_id] = user_data
                logger.info(
                    f'Awarding {current_gold_award} gold to {user_id} {event.author} and updating last earned time to {user_data["last_earned"]}'
                )
                print(f"Vault updated for {user_data} {event.author}")  #! Debug print statement
                # Save the modified vault
                async with aiofiles.open("forgesight_vault.json", "w") as file:
                    await file.write(json.dumps(vault, indent=4))
        else:
            print("Message was not long enough for rewards")
    else:
        print(f"Gold rewards are disabled. Message not awarded in {event.channel.id}")


# Grant gold to a user
@bot.tree.command(
    name="grant_gold",
    description="Grant gold to a user\n Usage: /grant_gold <@user> <amount of gold>",
)
@is_mod_or_admin()
async def grant_gold(
    Interaction: discord.Interaction, user: discord.Member, amount: int
):
    # Open the vault and retrieve the user's data
    async with aiofiles.open("forgesight_vault.json", "r") as file:
        data = await file.read()
        vault = json.loads(data) if data else {}
    user_id = str(user.id)
    user_data = vault.get(user_id, {"gold": 0, "last_earned": 0})
    # Add the gold to the user's balance
    user_data["gold"] += amount
    vault[user_id] = user_data
    # Save the modified vault
    async with aiofiles.open("forgesight_vault.json", "w") as file:
        await file.write(json.dumps(vault, indent=4))
    await Interaction.response.send_message(
        f"{amount} gold granted to {user.mention}.", ephemeral=False
    )
    logger.info(f"{amount} gold granted to {user} by {Interaction.user}")


@bot.tree.command(
    name="deduct_gold",
    description="Deduct gold from a user\n Usage: /deduct_gold <@user> <amount of gold>",
)
@is_mod_or_admin()
async def deduct_gold(
    Interaction: discord.Interaction, user: discord.Member, amount: int
):
    # Open the vault and retrieve the user's data
    async with aiofiles.open("forgesight_vault.json", "r") as file:
        data = await file.read()
        vault = json.loads(data) if data else {}
    user_id = str(user.id)
    user_data = vault.get(user_id, {"gold": 0, "last_earned": 0})
    # Check if the user has enough gold to deduct
    if user_data["gold"] < amount:
        await Interaction.response.send_message(
            f"{user.mention} does not have enough gold to deduct {amount} gold.",
            ephemeral=False,
        )
        return
    # Deduct the gold from the user's balance
    user_data["gold"] -= amount
    vault[user_id] = user_data
    # Save the modified vault
    async with aiofiles.open("forgesight_vault.json", "w") as file:
        await file.write(json.dumps(vault, indent=4))
    await Interaction.response.send_message(
        f"{amount} gold deducted from {user.mention}.", ephemeral=False
    )
    logger.info(f"{amount} gold deducted from {user} by {Interaction.user}")


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
    config_vals['GOLD_AWARD'] = number_of_gold
    await Interaction.response.send_message(
        f"Gold reward per message set to {config_vals['GOLD_AWARD']}", ephemeral=False
    )
    logger.info(f"Gold reward per message set to {config_vals['GOLD_AWARD']} by {Interaction.user}")


@bot.tree.command(
    name="configuration",
    description="Displays the current Forgesight configuration. \n Usage: /configuration",
)
@is_mod_or_admin()
async def get_configuration(Interaction: discord.Interaction):
    embed = discord.Embed(
        title="Forgesight Configuration",
        description="Current Configuration Values",
        color=0xCF2702,
    )
    embed.add_field(
        name="MIN_MESSAGE_REQUIRED", value=str(config_vals['MIN_MESSAGE_REQUIRED']), inline=False
    )
    embed.add_field(
        name="MIN_MESSAGE_LENGTH", value=config_vals['MIN_MESSAGE_LENGTH'], inline=False
    )
    embed.add_field(name="REWARDS", value=str(config_vals['REWARDS']), inline=False)
    embed.add_field(
        name="MESSAGE_REWARD_TIMEOUT", value=str(config_vals['MESSAGE_REWARD_TIMEOUT']), inline=False
    )
    embed.add_field(
        name="SUBSCRIBER_ROLE_ID", value=str(config_vals['SUBSCRIBER_ROLE_ID']), inline=False
    )
    embed.add_field(name="SUBSCRIBER_BONUS", value=str(config_vals['SUBSCRIBER_BONUS']), inline=False)
    embed.add_field(name="MEDIA_BONUS", value=str(config_vals['MEDIA_BONUS']), inline=False)
    embed.add_field(name="GOLD_AWARD", value=str(config_vals['GOLD_AWARD']), inline=False)
    embed.add_field(
        name="ALLOWED_CHANNEL_IDs", value=str(config_vals['ALLOWED_CHANNEL_IDs']), inline=False
    )
    await Interaction.response.send_message(embed=embed)


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
