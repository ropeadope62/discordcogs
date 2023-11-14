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
from discord.ext import commands

# Global variables for the bot - these can be changed with slash commands
# TODO: Write these variables to file so they persist between bot restarts
# TODO: Write a backup task for forgesight_vault.json

MIN_MESSAGE_REQUIRED = True
MIN_MESSAGE_LENGTH = 20
REWARDS = True
MESSAGE_REWARD_TIMEOUT = 10
SUBSCRIBER_ROLE_ID = 1074071214022201378
SUBSCRIBER_BONUS = 2
MEDIA_BONUS = 2
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


# Utility function for checking if a user is a mod or admin
def is_mod_or_admin():
    async def predicate(ctx):
        mod_role = discord.utils.get(ctx.guild.roles, name="Moderation Team")
        admin_role = discord.utils.get(ctx.guild.roles, name="Owner")
        return mod_role in ctx.author.roles or admin_role in ctx.author.roles

    return commands.check(predicate)


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
    description="Forgesight - Community engagement bot for Tableflip Foundry.",
)
async def forgesight_command(ctx):
    pass  # This is just to define the group, no action needed here.


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
    global MIN_MESSAGE_LENGTH
    MIN_MESSAGE_LENGTH = min_message_length
    await Interaction.response.send_message(
        f"Minimum message length for Gold reward has been set to {MIN_MESSAGE_LENGTH}.",
        ephemeral=False,
    )
    logger.info(
        f"Minimum message length set to {MIN_MESSAGE_LENGTH} by {Interaction.user}"
    )


@bot.tree.command(
    name="subscriber_bonus",
    description="Set the subscriber bonus applied to Gold rewards.",
)
@is_mod_or_admin()
async def set_subscriberbonus(Interaction: discord.Interaction, subscriber_bonus: int):
    global SUBSCRIBER_BONUS
    if subscriber_bonus < 0:
        await Interaction.response.send_message(
            f"Invalid subscriber bonus: {subscriber_bonus}. Subscriber bonus must be a positive integer.",
            ephemeral=True,
        )
        logger.warning(
            f"Invalid subscriber bonus entered by {Interaction.user} for /forgesight subscriberbonus command."
        )
        return
    SUBSCRIBER_BONUS = subscriber_bonus
    await Interaction.response.send_message(
        f"Subscriber bonus for Gold reward has been set to {SUBSCRIBER_BONUS}.",
        ephemeral=False,
    )
    logger.info(f"Subscriber bonus set to {SUBSCRIBER_BONUS} by {Interaction.user}")


@bot.tree.command(
    name="media_bonus", description="Set the media bonus applied to Gold rewards."
)
@is_mod_or_admin()
async def set_subscriberbonus(Interaction: discord.Interaction, media_bonus: int):
    global MEDIA_BONUS
    if media_bonus < 0:
        await Interaction.response.send_message(
            f"Invalid media bonus: {media_bonus}. Media bonus must be a positive integer.",
            ephemeral=True,
        )
        logger.warning(
            f"Invalid media bonus entered by {Interaction.user} for /forgesight media_bonus command."
        )
        return
    MEDIA_BONUS = media_bonus
    await Interaction.response.send_message(
        f"Media bonus for Gold reward has been set to {SUBSCRIBER_BONUS}.",
        ephemeral=False,
    )
    logger.info(f"Media bonus set to {SUBSCRIBER_BONUS} by {Interaction.user}")


@bot.tree.command(
    name="toggle_rewards",
    description="Toggle Gold rewards on or off. \n Usage: /toggle_rewards <on/off>",
)
@is_mod_or_admin()
async def toggle_rewards(Interaction: discord.Interaction, toggle: str):
    global REWARDS
    if toggle == "on":
        REWARDS = True
        await Interaction.response.send_message(
            f"Gold rewards have been turned on.", ephemeral=False
        )
        logger.info(f"Gold rewards have been turned on by {Interaction.user}")
    elif toggle == "off":
        REWARDS = False
        await Interaction.response.send_message(
            f"Gold rewards have been turned off.", ephemeral=False
        )
        logger.info(f"Gold rewards have been turned off by {Interaction.user}")
    else:
        await Interaction.response.send_message(
            f"Invalid option. Use 'on' or 'off'.", ephemeral=True
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
    global MESSAGE_REWARD_TIMEOUT
    if timeout < 0:
        await Interaction.response.send_message(
            f"Invalid timeout: {timeout}. Timeout must be a positive integer.",
            ephemeral=True,
        )
        logger.warning(
            f"Invalid timeout entered by {Interaction.user} for /forgesight reward_timeout command."
        )
        return
    MESSAGE_REWARD_TIMEOUT = timeout
    await Interaction.response.send_message(
        f"Message reward timeout set to {MESSAGE_REWARD_TIMEOUT} seconds.",
        ephemeral=False,
    )
    logger.info(
        f"Message reward timeout set to {MESSAGE_REWARD_TIMEOUT} by {Interaction.user}"
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
        )
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
            title=f"Gold Balance",
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


@bot.event
async def on_message(event):
    # We don't want the bot to reply to itself
    if event.author == bot:
        return
    if event.author.id == bot.user.id:
        return
    # Check that the rewards are enabled and that the message is in an allowed channel
    if REWARDS == True:
        vault = load_forgesight_vault()
        if event.channel.id not in ALLOWED_CHANNEL_IDs:
            print(
                f"Message not in allowed channel {event.channel.id}"
            )  #! Debug print statement, do not log this event due to spam
            return

        current_gold_award = GOLD_AWARD
        # Check if message length check is enabled
        if MIN_MESSAGE_REQUIRED:
            # If the message is long enough, award gold
            if len(event.content) >= MIN_MESSAGE_LENGTH:
                # If the user is a subscriber, apply the subscriber bonus
                if any(role.id == SUBSCRIBER_ROLE_ID for role in event.author.roles):
                    current_gold_award *= SUBSCRIBER_BONUS
                    print(
                        f"User {event.author.mention} has supporter role: Applying supporter bonus, new gold reward is {current_gold_award}"
                    )  #! Debug print statement
                # If the message has attachments, apply the media bonus
                if event.attachments:
                    current_gold_award *= MEDIA_BONUS
                    print(
                        f"Message has attachments: Applying media bonus, new gold reward is {current_gold_award}"
                    )  #! Debug print statement
                # Open the vault and retrieve the user's data
                async with aiofiles.open("forgesight_vault.json", "r") as file:
                    data = await file.read()
                    vault = json.loads(data) if data else {}
                user_id = str(event.author.id)
                user_data = vault.get(user_id, {"gold": 0, "last_earned": 0})
                # If the user has earned gold in the past MESSAGE_REWARD_TIMEOUT seconds, don't award gold
                if time.time() - user_data["last_earned"] < MESSAGE_REWARD_TIMEOUT:
                    print(
                        f"{event.author.mention} has already earned gold in the past {MESSAGE_REWARD_TIMEOUT} seconds."
                    )  #! Debug print statement
                    return
                # Award the gold and update the vault with new gold and last earned time
                user_data["gold"] += current_gold_award
                print(
                    f"Message was length {len(event.content)}: Awarding {current_gold_award} gold to {user_id}"
                )  #! Debug print statement
                user_data["last_earned"] = time.time()
                print(
                    f'Setting last earned time to {user_data["last_earned"]}'
                )  #! Debug print statement
                vault[user_id] = user_data
                logger.info(
                    f'Awarding {current_gold_award} gold to {user_id} and updating last earned time to {user_data["last_earned"]}'
                )
                print(f"Vault updated for {user_data}")  #! Debug print statement
                # Save the modified vault
                async with aiofiles.open("forgesight_vault.json", "w") as file:
                    await file.write(json.dumps(vault, indent=4))
        else:
            print(f"Message was not long enough for rewards")
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
    global GOLD_AWARD
    GOLD_AWARD = number_of_gold
    await Interaction.response.send_message(
        f"Gold reward per message set to {GOLD_AWARD}", ephemeral=False
    )
    logger.info(f"Gold reward per message set to {GOLD_AWARD} by {Interaction.user}")


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
        name="MIN_MESSAGE_REQUIRED", value=str(MIN_MESSAGE_REQUIRED), inline=False
    )
    embed.add_field(
        name="MIN_MESSAGE_LENGTH", value=str(MIN_MESSAGE_LENGTH), inline=False
    )
    embed.add_field(name="REWARDS", value=str(REWARDS), inline=False)
    embed.add_field(
        name="MESSAGE_REWARD_TIMEOUT", value=str(MESSAGE_REWARD_TIMEOUT), inline=False
    )
    embed.add_field(
        name="SUBSCRIBER_ROLE_ID", value=str(SUBSCRIBER_ROLE_ID), inline=False
    )
    embed.add_field(name="SUBSCRIBER_BONUS", value=str(SUBSCRIBER_BONUS), inline=False)
    embed.add_field(name="MEDIA_BONUS", value=str(MEDIA_BONUS), inline=False)
    embed.add_field(name="GOLD_AWARD", value=str(GOLD_AWARD), inline=False)
    embed.add_field(
        name="ALLOWED_CHANNEL_IDs", value=str(ALLOWED_CHANNEL_IDs), inline=False
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
