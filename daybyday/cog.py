import discord
import asyncio
import datetime
from redbot.core import commands, Config
from .views import DayByDayMenuView  # Import your view classes

class DayByDayCog(commands.Cog):
    """
    A cog to help users track their day-by-day progress by maintaining streaks,
    logging challenges, and updating their current mood.
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=987654321, force_registration=True)
        default_user = {
            "target": None,
            "goal": None,
            "mood": None,
            "streak": 0,
            "last_checkin": None,  # YYYY-MM-DD
            "rewards": [],
            "challenges": []
        }
        self.config.register_user(**default_user)
        self.milestones = {
            1: "Congratulations on 1 day of progress!",
            7: "Fantastic! 1 week into your journey!",
            30: "Amazing! 1 month of positive change!",
            90: "Incredible! 3 months strong!",
            180: "Outstanding! 6 months of commitment!",
            365: "Life-changing! 1 year of transformation!"
        }

    async def generate_main_menu_embed(self, user: discord.Member) -> discord.Embed:
        data = await self.config.user(user).all()
        embed = discord.Embed(
            title="Day-by-Day Progress Menu",
            description="Welcome to your progress dashboard. Choose an action below.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Target", value=data.get("target") or "Not set", inline=False)
        embed.add_field(name="Goal", value=data.get("goal") or "Not set", inline=False)
        embed.add_field(name="Current Mood", value=data.get("mood") or "Not set", inline=False)
        embed.add_field(name="Current Streak", value=data.get("streak") or 0, inline=False)
        challenges = data.get("challenges") or []
        embed.add_field(name="Challenges Logged", value=str(len(challenges)), inline=False)
        return embed

    # Helper methods (do_checkin, do_setback, etc.) can be defined here
    async def do_checkin(self, user: discord.Member) -> str:
        last_checkin = await self.config.user(user).last_checkin()
        now = datetime.datetime.utcnow().date()
        if last_checkin:
            try:
                last_date = datetime.datetime.strptime(last_checkin, "%Y-%m-%d").date()
            except Exception:
                last_date = None
        else:
            last_date = None

        if last_date == now:
            return "You have already checked in today!"
        if last_date and (now - last_date).days > 1:
            new_streak = 1
            result = "You missed a day. Your streak has been reset to 1."
        else:
            current_streak = await self.config.user(user).streak()
            new_streak = current_streak + 1
            result = f"Great job! Your streak is now {new_streak} day(s)."
        await self.config.user(user).streak.set(new_streak)
        await self.config.user(user).last_checkin.set(now.strftime("%Y-%m-%d"))

        if new_streak in self.milestones:
            reward_msg = self.milestones[new_streak]
            rewards = await self.config.user(user).rewards()
            if reward_msg not in rewards:
                rewards.append(reward_msg)
                await self.config.user(user).rewards.set(rewards)
                result += f"\nMilestone reached: {reward_msg}"
        return result

    # Define additional helper methods: do_setback, do_set_mood, do_log_challenge, etc.

    @commands.group(invoke_without_command=True, name="daybyday")
    async def daybyday(self, ctx: commands.Context):
        """Main menu for tracking your day-by-day progress."""
        from .views import DayByDayMenuView
        view = DayByDayMenuView(self, ctx)
        embed = await self.generate_main_menu_embed(ctx.author)
        view.message = await ctx.send(embed=embed, view=view)
        await view.initialize_menu()

    # Additional subcommands like setup, profile, setmood, checkin, setback, logchallenge can go here,
    # or if they’re simple enough, you can continue to use the interactive menu exclusively.
