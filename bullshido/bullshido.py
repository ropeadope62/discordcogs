# bullshido.py
import discord
import asyncio
from redbot.core import commands, Config
from .ui_elements import SelectFightingStyleView
from .fighting_game import FightingGame
from datetime import datetime, timedelta
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
        
        self.config.register_user(**default_user)
        
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
        pass

    @bullshido_group.command(name="log", description="Displays the log")
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    async def show_log(self, ctx: commands.Context):
        """Displays the Bullshido log."""
        logs = self.memory_handler.get_logs()
        if not logs:
            await ctx.send("No logs available.")
            return
        for chunk in [logs[i:i+10] for i in range(0, len(logs), 10)]:
            await ctx.send("```\n{}\n```".format("\n".join(chunk)))

    @bullshido_group.command(name="setstyle", description="Select your fighting style")
    async def select_fighting_style(self, ctx: commands.Context):
        """Prompts the user to select their fighting style."""
        view = SelectFightingStyleView(self.set_fighting_style, ctx.author, ctx)
        await ctx.send("Please select your fighting style:", view=view)
        
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
    async def train(self, ctx: commands.Context):
        """Train daily to increase your Bullshido training level."""
        self.logger.info(f"{ctx.author} used the train command.")
        user = ctx.author
        style = await self.config.user(user).fighting_style()
        
        # Check if the command was used in the last 24 hours
        last_train = await self.config.user(user).last_train()
        if last_train:
            last_train_time = datetime.strptime(last_train, '%Y-%m-%d %H:%M:%S')
            if datetime.utcnow() - last_train_time < timedelta(hours=24):
                await ctx.send(f"{user.mention}, you can only use the train command once every 24 hours.")
                return

        # Update the last train time before executing the command to avoid timing issues
        await self.config.user(user).last_train.set(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Increment training level
        new_training_level = await self.increment_training_level(user)
        self.logger.info(f"{user} has successfully trained in {style}! Their training level is now {new_training_level}.")
        await ctx.send(f"{user.mention} has successfully trained in {style}! Your training level is now {new_training_level}.")

    @bullshido_group.command(name="diet", description="Focus on your diet to increase your nutrition level")
    async def diet(self, ctx: commands.Context):
        """Focus on your diet to increase your nutrition level."""
        self.logger.info(f"{ctx.author} used the diet command.")
        user = ctx.author
        
        # Check if the command was used in the last 24 hours
        last_diet = await self.config.user(user).last_diet()
        if last_diet:
            last_diet_time = datetime.strptime(last_diet, '%Y-%m-%d %H:%M:%S')
            if datetime.utcnow() - last_diet_time < timedelta(hours=24):
                await ctx.send(f"{user.mention}, you can only use the diet command once every 24 hours.")
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
            color=0x00ff00
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
            value="Winning a fight increases your wins and morale. Losing decreases your morale. Keep training and dieting to improve your chances in future fights.",
            inline=False
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

    async def increment_training_level(self, user):
        self.logger.info(f"Incrementing training level for {user}")
        user_data = await self.config.user(user).all()
        new_training_level = user_data['training_level'] + 10
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

    async def increment_nutrition_level(self, user):
        self.logger.info(f"Incrementing nutrition level for {user}")
        user_data = await self.config.user(user).all()
        new_nutrition_level = user_data['nutrition_level'] + 10
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
    

    @bullshido_group.command(name="clear_old_config", description="Clears old configuration to avoid conflicts")
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    async def clear_old_config(self, ctx: commands.Context):
        """Clears old configuration to avoid conflicts."""
        await self.config.clear_all_users()
        await ctx.send("Old Bullshido configuration has been cleared.")
async def setup(bot):
    await bot.add_cog(Bullshido(bot))