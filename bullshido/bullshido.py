# bullshido.py
import discord
import asyncio
from redbot.core import commands, Config, bank
from .ui_elements import SelectFightingStyleView
from .fighting_game import FightingGame
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageTransform
from .fighting_constants import INJURY_TREATMENT_COST
import logging
import os

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

class Bullshido(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=123123451514345671215451351235890, force_registration=True)
        default_user = {
            "fighting_style": None,
            "wins": {"UD": 0, "SD": 0, "TKO": 0, "KO": 0},
            "losses": {"UD": 0, "SD": 0, "TKO": 0, "KO": 0},
            "level": 1,
            "training_level": 1,
            "nutrition_level": 1,
            "morale": 100,
            "intimidation_level": 0,
            "stamina_level": 100,
            "last_interaction": None,
            "last_command_used": None,
            "last_train": None,
            "last_diet": None,
            "fight_history": []
        }
        
        default_guild = {
            "rounds": 3,
            "max_strikes_per_round": 5,
            "training_weight": 0.15,
            "diet_weight": 0.15,
            "max_health": 100,
            "action_cost": 10,
            "base_miss_probability": 0.15,
            "base_stamina_cost": 10
        }
        
        self.config.register_user(**default_user)
        self.config.register_guild(**default_guild)
        
        self.logger = logging.getLogger("red.bullshido")
        self.logger.setLevel(logging.DEBUG)
        
        self.memory_handler = MemoryLogHandler()
        self.logger.addHandler(self.memory_handler)
        
        log_dir = os.path.expanduser("~/ScrapGPT/ScrapGPT/logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, "bullshido.log")

        self.file_handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)
        
        self.bg_task = self.bot.loop.create_task(self.check_inactivity())
        self.logger.info("Bullshido cog loaded.")
        
    async def has_sufficient_stamina(self, user):
        """ Check if the user has sufficient stamina to fight."""
        self.logger.info(f"Checking if {user} has sufficient stamina...")
        stamina = await self.config.user(user).stamina_level()
        return stamina >= 20
    
    async def add_permanent_injury(self, user: discord.Member, injury: str):
        """Add a permanent injury to a user."""
        async with self.config.user(user).permanent_injuries() as injuries:
            injuries.append(injury)

    async def get_permanent_injuries(self, user: discord.Member):
        """Get the list of permanent injuries for a user."""
        return await self.config.user(user).permanent_injuries()

    async def remove_permanent_injury(self, user: discord.Member, injury: str):
        """Remove a permanent injury from a user."""
        async with self.config.user(user).permanent_injuries() as injuries:
            if injury in injuries:
                injuries.remove(injury)
    
    def is_admin_or_mod():
        async def predicate(ctx):
            return ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.manage_guild
        return commands.check(predicate)
    
    async def set_fighting_style(self, interaction: discord.Interaction, new_style: str):
        user = interaction.user
        user_data = await self.config.user(user).all()

        if user_data["fighting_style"] != new_style:
            user_data["fighting_style"] = new_style
            user_data["training_level"] = 0
            await self.config.user(user).set(user_data)
            await self.config.user(user).fighting_style.set(new_style)
            await self.config.user(user).training_level.set(0)
            self.logger.info(f"{user} has changed their fighting style to {new_style}.")
            result = f"Fighting style changed to {new_style} and training level reset to 0."
        else:
            self.logger.warning(f"{user} already has the fighting style {new_style}.")
            result = "You already have this fighting style."

        await interaction.response.send_message(result)

    async def check_inactivity(self):
        self.logger.info("Checking for inactivity...")
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await self.apply_inactivity_penalties()
            await asyncio.sleep(3600)  # Check every hour

    async def apply_inactivity_penalties(self):
        self.logger.info("Applying inactivity penalties...")
        current_time = datetime.utcnow()
        async with self.config.all_users() as users:
            for user_id, user_data in users.items():
                self.logger.info(f"Applying inactivity penalties for user {user_id}")
                await self.apply_penalty(user_id, user_data, current_time, "train", "training_level")
                await self.apply_penalty(user_id, user_data, current_time, "diet", "nutrition_level")

    async def apply_penalty(self, user_id, user_data, current_time, last_action_key, level_key):
        last_action = user_data.get(f"last_{last_action_key}")
        if last_action:
            last_action_time = datetime.strptime(last_action, '%Y-%m-%d %H:%M:%S')
            if current_time - last_action_time > timedelta(days=2):
                # Apply penalty if the user missed a day
                new_level = max(1, user_data[level_key] - 20)
                await self.config.user_from_id(user_id)[level_key].set(new_level)
                user = self.bot.get_user(user_id)
                if user:
                    await user.send(f"You've lost 20 points in your {level_key.replace('_', ' ')} due to inactivity.")
                await self.config.user_from_id(user_id)[f"last_{last_action_key}"].set(current_time.strftime('%Y-%m-%d %H:%M:%S'))

    async def update_intimidation_level(self, user: discord.Member):
        self.logger.info(f"Updating intimidation level for {user}")
        user_data = await self.config.user(user).all()
        ko_wins = user_data["wins"]["KO"]
        tko_wins = user_data["wins"]["TKO"]
        intimidation_level = ko_wins + tko_wins
        self.logger.info(f"Intimidation level for {user} is {intimidation_level}")
        await self.config.user(user).intimidation_level.set(intimidation_level)

    @commands.hybrid_group(name="bullshido", description="Commands related to the Bullshido game")
    async def bullshido_group(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bullshido_help)

    @bullshido_group.command(name="set_rounds", description="Set the number of rounds in a fight.")
    @is_admin_or_mod()
    async def set_rounds(self, ctx: commands.Context, rounds: int):
        await self.config.guild(ctx.guild).rounds.set(rounds)
        await ctx.send(f"Number of rounds set to {rounds}.")
        
    @bullshido_group.command(name="set_max_strikes_per_round", description="Set the maximum number of strikes per round.")
    @is_admin_or_mod()
    async def set_max_strikes_per_round(self, ctx: commands.Context, max_strikes_per_round: int):
        await self.config.guild(ctx.guild).max_strikes_per_round.set(max_strikes_per_round)
        await ctx.send(f"Maximum number of strikes per round set to {max_strikes_per_round}.")
        
    @bullshido_group.command(name="set_training_weight", description="Set the training weight.")
    @is_admin_or_mod()
    async def set_training_weight(self, ctx: commands.Context, training_weight: float):
        await self.config.guild(ctx.guild).training_weight.set(training_weight)
        await ctx.send(f"Training weight set to {training_weight}.")
        
    @bullshido_group.command(name="set_diet_weight", description="Set the diet weight.")
    @is_admin_or_mod()
    async def set_diet_weight(self, ctx: commands.Context, diet_weight: float):
        await self.config.guild(ctx.guild).diet_weight.set(diet_weight)
        await ctx.send(f"Diet weight set to {diet_weight}.")
        
    @bullshido_group.command(name="set_max_health", description="Set the maximum health.")
    @is_admin_or_mod()
    async def set_max_health(self, ctx: commands.Context, max_health: int):
        await self.config.guild(ctx.guild).max_health.set(max_health)
        await ctx.send(f"Maximum health set to {max_health}.")
        
    @bullshido_group.command(name="set_action_cost", description="Set the action cost.")
    @is_admin_or_mod()
    async def set_action_cost(self, ctx: commands.Context, action_cost: int):
        await self.config.guild(ctx.guild).action_cost.set(action_cost)
        await ctx.send(f"Action cost set to {action_cost}.")
    
    @bullshido_group.command(name="set_base_miss_probability", description="Set the base miss probability.")
    @is_admin_or_mod()
    async def set_base_miss_probability(self, ctx: commands.Context, base_miss_probability: float):
        await self.config.guild(ctx.guild).base_miss_probability.set(base_miss_probability)
        await ctx.send(f"Base miss probability set to {base_miss_probability}.")
        
    
    @bullshido_group.command(name="set_base_stamina_cost", description="Set the base stamina cost.")
    @is_admin_or_mod()
    async def set_base_stamina_cost(self, ctx: commands.Context, base_stamina_cost: int):
        await self.config.guild(ctx.guild).base_stamina_cost.set(base_stamina_cost)
        await ctx.send(f"Base stamina cost set to {base_stamina_cost}.")
        
    @bullshido_group.command(name="log", description="Displays the log")
    @is_admin_or_mod()
    async def show_log(self, ctx: commands.Context):
        """Displays the Bullshido log."""
        logs = self.memory_handler.get_logs()
        if not logs:
            await ctx.send("No logs available.")
            return
        for chunk in [logs[i:i+10] for i in range(0, len(logs), 10)]:
            await ctx.send("```\n{}\n```".format("\n".join(chunk)))
            
    @bullshido_group.command(name="injuries", description="View your permanent injuries that require treatment.", aliases = ["injury", "inj"])
    async def permanent_injuries(self, ctx: commands.Context):
        """View your permanent injuries that require treatment."""
        user = ctx.author
        user_data = await self.config.user(user).all()
        permanent_injuries = user_data.get("permanent_injuries", [])

        if not permanent_injuries:
            await ctx.send("You have no permanent injuries.")
            return

        embed = discord.Embed(title=f"{user.display_name}'s Permanent Injuries", color=0xFF0000)
        for injury in permanent_injuries:
            embed.add_field(name="Injury", value=injury, inline=False)

        embed.set_thumbnail(url="https://i.ibb.co/7KK90YH/bullshido.png")
        await ctx.send(embed=embed)

    @bullshido_group.command(name="treat", description="Treat a permanent injury")
    async def treat(self, ctx: commands.Context, *, injury: str):
        """Treat a permanent injury."""
        user = ctx.author
        user_data = await self.config.user(user).all()
        permanent_injuries = user_data.get("permanent_injuries", [])
        
        if injury not in permanent_injuries:
            await ctx.send("You do not have this injury.")
            return

        cost = INJURY_TREATMENT_COST.get(injury)
        if cost is None:
            await ctx.send("This injury cannot be treated.")
            return

        balance = await bank.get_balance(user)
        if balance < cost:
            await ctx.send(f"You do not have enough credits to treat this injury. You need {cost} credits.")
            return

        await bank.withdraw_credits(user, cost)
        permanent_injuries.remove(injury)
        await self.config.user(user).permanent_injuries.set(permanent_injuries)

        await ctx.send(f"Successfully treated {injury}. Your new balance is {balance - cost} credits.")
    
    @bullshido_group.command(name="rankings", description="Top fighters in the Bullshido Kumatae.", aliases = ["rank", "leaderboard", "lb"])
    async def rankings(self, ctx: commands.Context):
        """Displays the top 25 players based on win-loss ratio and their fight record."""
        server_name = ctx.guild.name
        users = await self.config.all_users()
        ranking_list = []
            
        for user_id, user_data in users.items():
            wins = sum(user_data["wins"].values())
            losses = sum(user_data["losses"].values())
            if wins == 0 and losses == 0:
                continue  # Skip players with no fights
            if losses == 0:
                win_loss_ratio = wins  # Avoid division by zero
            else:
                win_loss_ratio = wins / losses
            
            ranking_list.append((user_id, wins, losses, win_loss_ratio))
            
            # Sort the list by win-loss ratio in descending order and take the top 25
        ranking_list = sorted(ranking_list, key=lambda x: x[3], reverse=True)[:25]

        embed = discord.Embed(title=f"{server_name} Bullshido Rankings", color=0xFF0000)
        embed.set_thumbnail(url="https://i.ibb.co/7KK90YH/bullshido.png")
           
        for i, (user_id, wins, losses, ratio) in enumerate(ranking_list, 1):
            user = self.bot.get_user(user_id)
            if user:
                embed.add_field(name=f"{i}. {user.display_name}",value=f"Wins: {wins}, Losses: {losses}",inline=False)

        await ctx.send(embed=embed)


    @bullshido_group.command(name="setstyle", description="Select your fighting style")
    async def select_fighting_style(self, ctx: commands.Context):
        """Prompts the user to select their fighting style."""
        view = SelectFightingStyleView(self.set_fighting_style, ctx.author, ctx)
        await ctx.send("Please select your fighting style:", view=view)
        
    @bullshido_group.command(name="list_fighting_styles", description="List all available fighting styles")
    async def list_fighting_styles(self, ctx: commands.Context):
        """List all available fighting styles."""
        styles = ["Karate", "Muay-Thai", "Aikido", "Boxing", "Kung-Fu", "Judo", "Taekwondo", "Wrestling", "Sambo", "MMA", "Capoeira", "Kickboxing", "Krav-Maga", "Brazilian Jiu-Jitsu"]
        embed = discord.Embed(title="Available Fighting Styles", description="\n".join(styles), color=0xFF0000)
        embed.set_thumbnail(url="https://i.ibb.co/7KK90YH/bullshido.png")
        await self.channel.send(embed=embed)
        
    @bullshido_group.command(name="fight", description="Start a fight with another player")
    async def fight(self, ctx: commands.Context, opponent: discord.Member):
        """Start a fight with another player."""
        await ctx.defer()
        try:
            player1 = ctx.author
            player2 = opponent

            player1_data = await self.config.user(player1).all()
            player2_data = await self.config.user(player2).all()

            if not await self.has_sufficient_stamina(player1):
                await ctx.send(f"You are too tired to fight,  {player1.mention}.\n Try waiting some time for your stamina to recover, or buy some supplements to speed up your recovery.")
                return
            if not await self.has_sufficient_stamina(player2):
                await ctx.send("Your opponent does not have enough stamina to start the fight.")
                return

            if not player1_data['fighting_style'] or not player2_data['fighting_style']:
                await ctx.send("Both players must have selected a fighting style before starting a fight.")
                return
            if player1 == player2:
                await ctx.send("You cannot fight yourself, only your own demons! Try challenging another fighter.")
                return

            # Set up an instance of game session
            game = FightingGame(self.bot, ctx.channel, player1, player2, player1_data, player2_data, self)
            await game.start_game()

        except Exception as e:
            self.logger.error(f"Failed to start fight: {e}")
            await ctx.send(f"Failed to start the fight due to an error: {e}")

    @bullshido_group.command(name="train", description="Train daily to increase your Bullshido training level")
    async def train(self, ctx: commands.Context, user):
        """Train daily to increase your Bullshido training level."""
        self.logger.info(f"{ctx.author} used the train command.")
        user = ctx.author
        style = await self.config.user(user).fighting_style()
        
        # Check if the command was used in the last 24 hours
        last_train = await self.config.user(user).last_train()
        if last_train:
            last_train_time = datetime.strptime(last_train, '%Y-%m-%d %H:%M:%S')
            time_since_last_train = datetime.utcnow() - last_train_time
            if time_since_last_train < timedelta(hours=24):
                time_left = timedelta(hours=24) - time_since_last_train
                hours, remainder = divmod(time_left.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                await ctx.send(f"{user.mention}, you can only use the train command once every 24 hours. Time left: {time_left.days} days, {hours} hours, and {minutes} minutes.")
                return

        # Update the last train time before executing the command to avoid timing issues
        await self.config.user(user).last_train.set(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Increment training level
        new_training_level = await self.increment_training_level(user)
        self.logger.info(f"{user} has successfully trained in {style}! Their training level is now {new_training_level}.")
        await ctx.send(f"{user.mention} has successfully trained in {style}! Your training level is now {new_training_level}.")

    @bullshido_group.command(name="diet", description="Focus on your diet to increase your nutrition level")
    async def diet(self, ctx: commands.Context, user):
        """Focus on your diet to increase your nutrition level."""
        self.logger.info(f"{ctx.author} used the diet command.")
        user = ctx.author
        
        # Check if the command was used in the last 24 hours
        last_diet = await self.config.user(user).last_diet()
        if last_diet:
            last_diet_time = datetime.strptime(last_diet, '%Y-%m-%d %H:%M:%S')
            time_since_last_diet = datetime.utcnow() - last_diet_time
            if time_since_last_diet < timedelta(hours=24):
                time_left = timedelta(hours=24) - time_since_last_diet
                hours, remainder = divmod(time_left.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                await ctx.send(f"{user.mention}, you can only use the diet command once every 24 hours. Time left: {time_left.days} days, {hours} hours, and {minutes} minutes.")
                return

        # Update the last diet time before executing the command to avoid timing issues
        await self.config.user(user).last_diet.set(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Increment nutrition level
        new_nutrition_level = await self.increment_nutrition_level(user)
        await ctx.send(f"{user.mention} has followed their specialized diet today and gained nutrition level! Your nutrition level is now {new_nutrition_level}.")
    
    @bullshido_group.command(name="help", description="Learn how the Bullshido game works")
    async def bullshido_help(self, ctx: commands.Context):
        """Provides information about how the Bullshido game works."""
        embed = discord.Embed(
            title="About Bullshido",
            description="Welcome to Bullshido, a Discord game of epic combat!",
            color=0xFF0000
        )
        embed.add_field(
            name="Selecting a Fighting Style",
            value="Use `/bullshido select_fighting_style` to choose your fighting style. Each style has unique strikes and abilities.",
            inline=False
        )
        embed.add_field(
            name="Daily Training and Diet",
            value="Train and follow a diet each day to improve your stats:\n- `/bullshido train`: Train daily to increase your training level.\n- `/bullshido diet`: Follow a diet to increase your nutrition level.\n*Note: Each can be used once every 24 hours.*\n Your overall nutrition and training level will improve your chances of winning a fight.",
            inline=False
        )
        embed.add_field(
            name="Starting a Fight",
            value="Challenge another player to a fight using `/bullshido fight @player`. The fight consists of 3 rounds and will be scored by a panel of judges, unless a KO/TKO/Submission occurs.",
            inline=False
        )
        embed.add_field(
            name="Winning and Losing",
            value="Winning a fight increases your wins and morale and may also increase your intimidation level. Losing decreases your morale. Keep training and dieting to improve your chances in future fights.",
            inline=False
        )
        embed.add_field(
            name="How Damage is Calculated",
        value="Damage is calculated using your fighting style, stats and stamina. Training level and nutrition level affect damage by 15%.",
        )
        embed.add_field(
            name="How Misses and Blocks are Calculated", 
            value="Misses and blocks are calculated using the attacker and defender's training level and stamina. Training level and nutrition level affect misses and blocks by up to50%.",
        )
        embed.add_field(
            name="Penalties for Inactivity",
            value="If you miss a day of training or diet, your stats will decrease by 20 points.",
            inline=False
        )
        embed.add_field(
            name="Fighting Styles",
            value="Each style has unique strikes and abilities. Use `/bullshido list_fighting_styles` to see all available styles.",
        )
        embed.add_field(
            name="Stamina",
            value="Fighting costs stamina, which will be regained daily, or can be replenished by purchasing stamina recovery items. Use `/bullshido stamina` to see your current stamina level.",
        )
        embed.add_field(
            name="Buy",
            value="Buy stamina recovery items using `/bullshido buy <item>`.",
        )
        embed.set_thumbnail(url="https://i.ibb.co/GWpXztm/bullshido.png")
        await ctx.send(embed=embed)


    @bullshido_group.command(name="reset_stats", description="Resets all Bullshido user data to default values")
    @is_admin_or_mod()
    async def reset_stats(self, ctx: commands.Context):
        """Reset the Bullshido Redbot Configuration values to default for all users."""
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.upper() == "YES"

        # Send confirmation message
        await ctx.send("Are you sure you want to reset Bullshido user data? Type 'YES' to confirm.")

        try:
            # Wait for a response for 30 seconds
            confirmation = await self.bot.wait_for('message', check=check, timeout=30.0)
            if confirmation:
                # If confirmed, reset all config values
                default_user = {
                    "fighting_style": None,
                    "wins": {"UD": 0, "SD": 0, "TKO": 0, "KO": 0},
                    "losses": {"UD": 0, "SD": 0, "TKO": 0, "KO": 0},
                    "level": 1,
                    "training_level": 1,
                    "nutrition_level": 1,
                    "morale": 100,
                    "intimidation_level": 0,
                    "stamina_level": 100,
                    "last_interaction": None,
                    "last_command_used": None,
                    "last_train": None,
                    "last_diet": None,
                    "fight_history": []
                }

                async with self.config.all_users() as all_users:
                    for user_id in all_users:
                        user_config = self.config.user_from_id(user_id)
                        for key, value in default_user.items():
                            await user_config.set_raw(key, value=value)

                await ctx.send("All config values have been reset to default.")
        except asyncio.TimeoutError:
            await ctx.send("Reset operation cancelled due to timeout.")

    @bullshido_group.command(name="reset_config", description="Resets Bullshido configuration to default values")
    @is_admin_or_mod()
    async def reset_config(self, ctx: commands.Context):
        """Resets Bullshido configuration to default values."""
        await self.config.clear_all_users()
        await ctx.send("Bullshido configuration has been reset to default values.")

    @bullshido_group.command(name="player_stats", description="Displays your wins and losses", aliases=["stats"])
    async def player_stats(self, ctx: commands.Context):
        """Displays your wins and losses."""
        user = ctx.author
        wins = await self.config.user(user).wins()
        losses = await self.config.user(user).losses()
        level = await self.config.user(user).level()
        training_level = await self.config.user(user).training_level()
        nutrition_level = await self.config.user(user).nutrition_level()
        morale = await self.config.user(user).morale()
        intimidation_level = await self.config.user(user).intimidation_level()
        fighting_style = await self.config.user(user).fighting_style()
        stamina = await self.config.user(user).stamina_level()

        total_wins = sum(wins.values())
        total_losses = sum(losses.values())

        embed = discord.Embed(title=f"{user.display_name}'s Fight Record", color=0xFF0000)
        embed.add_field(name="Total Wins", value=total_wins, inline=True)
        embed.add_field(name="Total Losses", value=total_losses, inline=True)
        embed.add_field(name="Wins (UD)", value=wins["UD"], inline=True)
        embed.add_field(name="Wins (SD)", value=wins["SD"], inline=True)
        embed.add_field(name="Wins (TKO)", value=wins["TKO"], inline=True)
        embed.add_field(name="Wins (KO)", value=wins["KO"], inline=True)
        embed.add_field(name="Losses (UD)", value=losses["UD"], inline=True)
        embed.add_field(name="Losses (SD)", value=losses["SD"], inline=True)
        embed.add_field(name="Losses (TKO)", value=losses["TKO"], inline=True)
        embed.add_field(name="Losses (KO)", value=losses["KO"], inline=True)
        embed.add_field(name=f"{user.display_name}'s Current Stats", value="\u200b", inline=False)
        embed.add_field(name="Fighting Style", value=fighting_style, inline=True)
        embed.add_field(name="Level", value=level, inline=True)
        embed.add_field(name="Training Level", value=training_level, inline=True)
        embed.add_field(name="Nutrition Level", value=nutrition_level, inline=True)
        embed.add_field(name="Morale", value=morale, inline=True)
        embed.add_field(name="Intimidation Level", value=intimidation_level, inline=True)
        embed.add_field(name="Stamina", value=stamina, inline=True)
        embed.set_thumbnail(url="https://i.ibb.co/7KK90YH/bullshido.png")
        await ctx.send(embed=embed)

    @bullshido_group.command(name="fight_record", description="Displays the results of your last 10 fights")
    async def fight_record(self, ctx: commands.Context):
        """Displays the results of your last 10 fights."""
        user = ctx.author
        fight_history = await self.config.user(user).fight_history()

        if not fight_history:
            await ctx.send("You have no fight history.")
            return

        embed = discord.Embed(title=f"{user.display_name}'s Last 10 Fights", color=0xFF0000)

        for fight in fight_history[-10:]:
            outcome = fight.get("outcome", "Unknown")
            opponent = fight.get("opponent", "Unknown")
            result_type = fight.get("result_type", "Unknown")
            embed.add_field(name=f"Fight vs {opponent}", value=f"Outcome: {outcome}, Result: {result_type}", inline=False)

        embed.set_thumbnail(url="https://i.ibb.co/7KK90YH/bullshido.png")
        await ctx.send(embed=embed)

    async def get_player_data(self, user):
        fighting_style = await self.config.user(user).fighting_style()
        level = await self.config.user(user).level()
        training_level = await self.config.user(user).training_level()
        nutrition_level = await self.config.user(user).nutrition_level()
        morale = await self.config.user(user).morale()
        intimidation_level = await self.config.user(user).intimidation_level()
        wins = await self.config.user(user).wins()
        losses = await self.config.user(user).losses()
        fight_history = await self.config.user(user).fight_history()
        return {
            "fighting_style": fighting_style,
            "wins": wins,
            "losses": losses,
            "level": level,
            "training_level": training_level,
            "nutrition_level": nutrition_level,
            "morale": morale,
            "intimidation_level": intimidation_level,
            "fight_history": fight_history
        }
    
    async def update_player_stats(self, user, win, result_type, opponent_name):
        try:
            current_wins = await self.config.user(user).wins()
            current_losses = await self.config.user(user).losses()
            fight_history = await self.config.user(user).fight_history()

            outcome = "Win" if win else "Loss"

            fight_history.append({
                "opponent": opponent_name,
                "outcome": outcome,
                "result_type": result_type
            })

            if win:
                new_wins = current_wins.copy()
                new_wins[result_type] += 1
                await self.config.user(user).wins.set(new_wins)
                self.logger.debug(f"Updated wins for {user.display_name}: {current_wins} -> {new_wins}")
            else:
                new_losses = current_losses.copy()
                new_losses[result_type] += 1
                await self.config.user(user).losses.set(new_losses)
                self.logger.debug(f"Updated losses for {user.display_name}: {current_losses} -> {new_losses}")

            # Update the fight history
            await self.config.user(user).fight_history.set(fight_history)
            await self.update_intimidation_level(user)

        except Exception as e:
            self.logger.error(f"Error updating stats for {user.display_name}: {e}")

    @bullshido_group.command(name="clear_old_config", description="Clears old configuration to avoid conflicts")
    @is_admin_or_mod()
    async def clear_old_config(self, ctx: commands.Context):
        """Clears old configuration to avoid conflicts."""
        await self.config.clear_all_users()
        await ctx.send("Old Bullshido configuration has been cleared.")
        
    @bullshido_group.command(name="test_fight_image")
    async def display_fight_image(self, ctx: commands.Context, player1: discord.Member, player2: discord.Member):
        try:
            # Create a dummy player data for testing
            player1_data = {
                "fighting_style": "Karate",
                "wins": {"UD": 5, "SD": 3, "TKO": 2, "KO": 1},
                "losses": {"UD": 2, "SD": 1, "TKO": 3, "KO": 4},
                "training_level": 3,
                "nutrition_level": 2,
                "morale": 80,
                "intimidation_level": 1,
                "stamina_level": 100,
                "last_interaction": None,
                "last_command_used": None,
                "last_train": None,
                "last_diet": None,
                "fight_history": []
            }
            
            player2_data = {
                "fighting_style": "Muay Thai",
                "wins": {"UD": 4, "SD": 5, "TKO": 3, "KO": 2},
                "losses": {"UD": 1, "SD": 2, "TKO": 2, "KO": 3},
                "training_level": 4,
                "nutrition_level": 3,
                "morale": 85,
                "intimidation_level": 2,
                "stamina_level": 100,
                "last_interaction": None,
                "last_command_used": None,
                "last_train": None,
                "last_diet": None,
                "fight_history": []
            }

            # Initialize the FightingGame instance with dummy data for testing
            game = FightingGame(self.bot, ctx.channel, player1, player2, player1_data, player2_data, self)

            fight_image_path = await game.generate_fight_image()
            await ctx.send(file=discord.File(fight_image_path))
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
        
    async def increment_training_level(self, ctx, user):
        self.logger.info(f"Incrementing training level for {user}")
        user_data = await self.config.user(user).all()
        new_training_level = min(100,user_data['training_level'] + 10)
        if new_training_level >= 100:
            await ctx.send(f"{user.mention} has reached maximum training level for the next 24 hours!")
        await self.config.user(user).training_level.set(new_training_level)
        self.logger.info(f"Training level for {user} is now {new_training_level}")
        return new_training_level
    
    async def increment_stamina_level(self, user):
        self.logger.info(f"Incrementing stamina level for {user}")
        stamina_level = await self.config.user(user).stamina_level()
        new_stamina_level = stamina_level + 10
        await self.config.user(user).training_level.set(new_stamina_level)
        self.logger.info(f"Stamina level for {user} is now {new_stamina_level}")
        return new_stamina_level

    async def increment_nutrition_level(self, ctx, user):
        self.logger.info(f"Incrementing nutrition level for {user}")
        user_data = await self.config.user(user).all()
        new_nutrition_level = min(100,user_data['nutrition_level'] + 10)
        if new_nutrition_level >= 100:
            await ctx.send(f"{user.mention} has reached optimal nutrition for the next 24 hours!")
        await self.config.user(user).nutrition_level.set(new_nutrition_level)
        self.logger.info(f"Nutrition level for {user} is now {new_nutrition_level}")
        return new_nutrition_level

    async def update_daily_interaction(self, user, command_used):
        self.logger.info(f"Updating daily interaction for {user}")
        user_data = await self.config.user(user).all()
        today = datetime.utcnow().date()
        
        last_interaction = user_data.get(f'last_{command_used}')
        if last_interaction:
            last_interaction_date = datetime.strptime(last_interaction, '%Y-%m-%d %H:%M:%S').date()
            self.logger.info(f"Last {command_used} interaction for {user} was on {last_interaction_date}.")
            if today - last_interaction_date > timedelta(days=1):
                await self.config.user(user).last_interaction.set(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
                self.logger.info(f"Reset last {command_used} interaction for {user}.")
    
    
    
    async def setup(bot):
        cog = Bullshido(bot)
        await bot.add_cog(cog)
        await bot.tree.sync()