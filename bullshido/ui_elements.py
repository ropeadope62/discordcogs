from discord import ui, ButtonStyle
import discord

class SelectFightingStyleView(ui.View):
    def __init__(self, on_fighting_style_selected, user):
        super().__init__()
        self.on_fighting_style_selected = on_fighting_style_selected
        self.user = user

    @ui.button(label="Aikido", style=ButtonStyle.primary, custom_id="aikido")
    async def handle_aikido(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.user, "aikido")
        await interaction.response.send_message("You have selected Aikido", ephemeral=True)
        self.stop()

    @ui.button(label="Boxing", style=ButtonStyle.primary, custom_id="boxing")
    async def handle_boxing(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.user, "boxing")
        await interaction.response.send_message("You have selected Boxing", ephemeral=True)
        self.stop()

    @ui.button(label="Kung-Fu", style=ButtonStyle.primary, custom_id="kungfu")
    async def handle_kungfu(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.user, "kungfu")
        await interaction.response.send_message("You have selected Kung-Fu", ephemeral=True)
        self.stop()

    @ui.button(label="Judo", style=ButtonStyle.primary, custom_id="judo")
    async def handle_judo(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.user, "judo")
        await interaction.response.send_message("You have selected Judo", ephemeral=True)
        self.stop()

    @ui.button(label="Taekwondo", style=ButtonStyle.primary, custom_id="taekwondo")
    async def handle_taekwondo(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.user, "taekwondo")
        await interaction.response.send_message("You have selected Taekwondo", ephemeral=True)
        self.stop()

    @ui.button(label="Wrestling", style=ButtonStyle.primary, custom_id="wrestling")
    async def handle_wrestling(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.user, "wrestling")
        await interaction.response.send_message("You have selected Wrestling", ephemeral=True)
        self.stop()

    @ui.button(label="Krav-Maga", style=ButtonStyle.primary, custom_id="kravmaga")
    async def handle_kravmaga(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.user, "kravmaga")
        await interaction.response.send_message("You have selected Krav-Maga", ephemeral=True)
        self.stop()

    @ui.button(label="Capoeira", style=ButtonStyle.primary, custom_id="capoeira")
    async def handle_capoeira(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.user, "capoeira")
        await interaction.response.send_message("You have selected Capoeira", ephemeral=True)
        self.stop()

    @ui.button(label="Sambo", style=ButtonStyle.primary, custom_id="sambo")
    async def handle_sambo(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.user, "sambo")
        await interaction.response.send_message("You have selected Sambo", ephemeral=True)
        self.stop()

    @ui.button(label="Kick-Boxing", style=ButtonStyle.primary, custom_id="kickboxing")
    async def handle_kickboxing(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.user, "kickboxing")
        await interaction.response.send_message("You have selected Kick-Boxing", ephemeral=True)
        self.stop()

    @ui.button(label="MMA", style=ButtonStyle.primary, custom_id="mma")
    async def handle_mma(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.user, "mma")
        await interaction.response.send_message("You have selected MMA", ephemeral=True)
        self.stop()
