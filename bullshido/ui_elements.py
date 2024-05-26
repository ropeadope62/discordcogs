from discord import ui, ButtonStyle, Button
import discord

class SelectFightingStyleView(ui.View):
    def __init__(self, on_fighting_style_selected, user, ctx):
        super().__init__(timeout=180)
        self.on_fighting_style_selected = on_fighting_style_selected
        self.user = user
        self.ctx = ctx
        
        fighting_styles = ["Karate", "Muay-Thai", "Aikido", "Boxing", "Kung-Fu", "Judo", "Taekwondo", "Wrestling", "Sambo", "MMA", "Capoeira", "Kickboxing", "Krav-Maga", "Brazilian Jiu-Jitsu"]
        for style in fighting_styles:
            self.add_item(Button(label=style, style=discord.ButtonStyle.primary, custom_id=style))

    @ui.button(label="Aikido", style=ButtonStyle.primary, custom_id="aikido")
    async def handle_aikido(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.ctx, self.user, "Aikido")
        await interaction.response.send_message("You have selected Aikido", ephemeral=True)
        self.stop()
        
    @ui.button(label="Karate", style=ButtonStyle.primary, custom_id="karate")
    async def handle_karate(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.ctx, self.user, "Karate")
        await interaction.response.send_message("You have selected Karate", ephemeral=True)
        self.stop()
        
    @ui.button(label="Muay-Thai", style=ButtonStyle.primary, custom_id="muaythai")
    async def handle_muaythai(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.ctx, self.user, "Muay-Thai")
        await interaction.response.send_message("You have selected Muay-Thai", ephemeral=True)
        self.stop()
    
    @ui.button(label="Brazilian Jiu-Jitsu", style=ButtonStyle.primary, custom_id="bjj")
    async def handle_bjj(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.ctx, self.user, "Brazilian Jiu-Jitsu")
        await interaction.response.send_message("You have selected Brazilian Jiu-Jitsu", ephemeral=True)
        self.stop()

    @ui.button(label="Boxing", style=ButtonStyle.primary, custom_id="boxing")
    async def handle_boxing(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.ctx, self.user, "Boxing")
        await interaction.response.send_message("You have selected Boxing", ephemeral=True)
        self.stop()

    @ui.button(label="Kung-Fu", style=ButtonStyle.primary, custom_id="kungfu")
    async def handle_kungfu(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.ctx, self.user, "Kung-Fu")
        await interaction.response.send_message("You have selected Kung-Fu", ephemeral=True)
        self.stop()

    @ui.button(label="Judo", style=ButtonStyle.primary, custom_id="judo")
    async def handle_judo(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.ctx, self.user, "Judo")
        await interaction.response.send_message("You have selected Judo", ephemeral=True)
        self.stop()

    @ui.button(label="Taekwondo", style=ButtonStyle.primary, custom_id="taekwondo")
    async def handle_taekwondo(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.ctx, self.user, "Taekwondo")
        await interaction.response.send_message("You have selected Taekwondo", ephemeral=True)
        self.stop()

    @ui.button(label="Wrestling", style=ButtonStyle.primary, custom_id="wrestling")
    async def handle_wrestling(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.ctx, self.user, "Wrestling")
        await interaction.response.send_message("You have selected Wrestling", ephemeral=True)
        self.stop()

    @ui.button(label="Krav-Maga", style=ButtonStyle.primary, custom_id="kravmaga")
    async def handle_kravmaga(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.ctx, self.user, "Krav-Maga")
        await interaction.response.send_message("You have selected Krav-Maga", ephemeral=True)
        self.stop()

    @ui.button(label="Capoeira", style=ButtonStyle.primary, custom_id="capoeira")
    async def handle_capoeira(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.ctx, self.user, "Capoeira")
        await interaction.response.send_message("You have selected Capoeira", ephemeral=True)
        self.stop()

    @ui.button(label="Sambo", style=ButtonStyle.primary, custom_id="sambo")
    async def handle_sambo(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.ctx, self.user, "Sambo")
        await interaction.response.send_message("You have selected Sambo", ephemeral=True)
        self.stop()

    @ui.button(label="Kickboxing", style=ButtonStyle.primary, custom_id="kickboxing")
    async def handle_kickboxing(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.ctx, self.user, "Kickboxing")
        await interaction.response.send_message("You have selected Kickboxing", ephemeral=True)
        self.stop()

    @ui.button(label="MMA", style=ButtonStyle.primary, custom_id="mma")
    async def handle_mma(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(self.ctx, self.user, "MMA")
        await interaction.response.send_message("You have selected MMA", ephemeral=True)
        self.stop()
