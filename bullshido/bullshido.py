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

        current_working_directory = os.getcwd()
        log_directory = os.path.join(current_working_directory, 'logs')
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        log_file_path = os.path.join(log_directory, 'bullshido.log')

        self.logger = logging.getLogger("red.bullshido")
        self.logger.setLevel(logging.DEBUG)

        self.memory_handler = MemoryLogHandler()
        self.logger.addHandler(self.memory_handler)

        self.file_handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)
        self.bg_task = self.bot.loop.create_task(self.check_inactivity())
        self.logger.info("Bullshido cog loaded.")

    async def has_sufficient_stamina(self, user):
        """ Check if the user has sufficient stamina to fight."""
        stamina = await self.config.user(user).stamina_level()
        self.logger.debug(f"Checking stamina for {user.display_name}: {stamina}")
        return stamina >= 20

    async def change_fighting_style(self, user: discord.Member, new_style: str):
        # Fetch User data
        user_data = await self.config.user(user).all()
        self.logger.debug(f"Changing fighting style for {user.display_name}: {user_data}")
        # Check if the user changed style 
        if user_data["fighting_style"] != new_style:
            # If new style is different, reset training 
            user_data["fighting_style"] = new_style
            self.logger.debug(f"New style detected- Resetting training level for {user.display_name}")
            user_data["training_level"] = 0
            # Update the config
            await self.config.user(user).set(user_data)
            await self.config.user(user).fighting_style.set(new_style)
            await self.config.user(user).training_level.set(0)

            return f"Fighting style changed to {new_style} and training level reset to 0."
        else:
            return "You already have this fighting style."

    async def check_inactivity(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await self.apply_inactivity_penalties()
            await asyncio.sleep(3600)  # Check every hour

    async def apply_inactivity_penalties(self):
        self.logger.debug("Applying inactivity penalties...")
        current_time = datetime.utcnow()
        async with self.config.all_users() as users:
            for user_id, user_data in users.items():
                self.logger.debug(f"Applying inactivity penalties for {user_id}: {user_data}")
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

    async def set_fighting_style(self, ctx: commands.Context, new_style):
        self.logger.debug(f"Setting fighting style for {ctx.author.display_name}: {new_style}")
        result = await self.change_fighting_style(ctx.author, new_style)
        await ctx.send(result)

    async def update_intimidation_level(self, user: discord.Member):
        self.logger.debug(f"Updating intimidation level for {user.display_name}")
        user_data = await self.config.user(user).all()
        ko_wins = user_data["wins"]["KO"]
        tko_wins = user_data["wins"]["TKO"]
        intimidation_level = ko_wins + tko_wins # submission wins to be added
        self.logger.debug(f"Intimidation level for {user.display_name}: {intimidation_level}")
        await self.config.user(user).intimidation_level.set(intimidation_level)

    @commands.hybrid_group(name="bullshido", description="Commands related to the Bullshido game")
    async def bullshido_group(self, ctx: commands.Context):
        pass

    @bullshido_group.command(name="log", description="Displays the log")
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
