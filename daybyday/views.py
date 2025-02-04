import discord
from discord.ext import commands
from .cog import DayByDayCog  # if you need type hints or access to helper methods

class DayByDayMenuView(discord.ui.View):
    def __init__(self, cog: DayByDayCog, ctx: commands.Context):
        super().__init__(timeout=180)
        self.cog = cog
        self.ctx = ctx
        self.message: discord.Message = None

    async def initialize_menu(self):
        # Any asynchronous initialization, if needed
        pass

    async def update_embed(self):
        new_embed = await self.cog.generate_main_menu_embed(self.ctx.author)
        await self.message.edit(embed=new_embed, view=self)

    @discord.ui.button(label="Profile", style=discord.ButtonStyle.primary, custom_id="daybyday_profile")
    async def profile_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("This is not your menu.", ephemeral=True)
        await self.update_embed()
        await interaction.response.send_message("Profile updated.", ephemeral=True)

    @discord.ui.button(label="Check-In", style=discord.ButtonStyle.success, custom_id="daybyday_checkin")
    async def checkin_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("This is not your menu.", ephemeral=True)
        result = await self.cog.do_checkin(interaction.user)
        await self.update_embed()
        await interaction.response.send_message(result, ephemeral=True)

    @discord.ui.button(label="Set Mood", style=discord.ButtonStyle.secondary, custom_id="daybyday_setmood")
    async def setmood_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("This is not your menu.", ephemeral=True)
        modal = SetMoodModal(self.cog, self.ctx.author, self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Log Challenge", style=discord.ButtonStyle.danger, custom_id="daybyday_logchallenge")
    async def logchallenge_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("This is not your menu.", ephemeral=True)
        modal = LogChallengeModal(self.cog, self.ctx.author, self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Setback", style=discord.ButtonStyle.blurple, custom_id="daybyday_setback")
    async def setback_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("This is not your menu.", ephemeral=True)
        result = await self.cog.do_setback(interaction.user)
        await self.update_embed()
        await interaction.response.send_message(result, ephemeral=True)

class SetMoodModal(discord.ui.Modal, title="Set Your Mood"):
    new_mood = discord.ui.TextInput(label="Your new mood", style=discord.TextStyle.short)

    def __init__(self, cog: DayByDayCog, user: discord.Member, view: DayByDayMenuView):
        self.cog = cog
        self.user = user
        self.view = view
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            return await interaction.response.send_message("This modal is not for you.", ephemeral=True)
        result = await self.cog.do_set_mood(self.user, self.new_mood.value)
        await self.view.update_embed()
        await interaction.response.send_message(result, ephemeral=True)

class LogChallengeModal(discord.ui.Modal, title="Log a Challenge"):
    challenge_details = discord.ui.TextInput(label="Describe your challenge", style=discord.TextStyle.long)

    def __init__(self, cog: DayByDayCog, user: discord.Member, view: DayByDayMenuView):
        self.cog = cog
        self.user = user
        self.view = view
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            return await interaction.response.send_message("This modal is not for you.", ephemeral=True)
        result = await self.cog.do_log_challenge(self.user, self.challenge_details.value)
        await self.view.update_embed()
        await interaction.response.send_message(result, ephemeral=True)
