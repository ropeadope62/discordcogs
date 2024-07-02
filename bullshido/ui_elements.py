from discord import ui, ButtonStyle
import discord

class SelectFightingStyleView(ui.View):
    def __init__(self, on_fighting_style_selected, user, ctx):
        super().__init__(timeout=180)
        self.on_fighting_style_selected = on_fighting_style_selected
        self.user = user
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.user

    async def on_fighting_style_selected(self, ctx, style: str):
        await ctx.bot.get_cog('Bullshido').set_fighting_style(ctx, style)

    @ui.button(label="Karate", style=ButtonStyle.primary)
    async def handle_karate(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(interaction, "Karate")

    @ui.button(label="Muay-Thai", style=ButtonStyle.primary)
    async def handle_muaythai(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(interaction, "Muay-Thai")
    
    @ui.button(label="Aikido", style=ButtonStyle.primary)
    async def handle_aikido(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(interaction, "Aikido")

    @ui.button(label="Boxing", style=ButtonStyle.primary)
    async def handle_boxing(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(interaction, "Boxing")

    @ui.button(label="Kung-Fu", style=ButtonStyle.primary)
    async def handle_kungfu(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(interaction, "Kung-Fu")

    @ui.button(label="Judo", style=ButtonStyle.primary)
    async def handle_judo(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(interaction, "Judo")

    @ui.button(label="Taekwondo", style=ButtonStyle.primary)
    async def handle_taekwondo(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(interaction, "Taekwondo")

    @ui.button(label="Wrestling", style=ButtonStyle.primary)
    async def handle_wrestling(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(interaction, "Wrestling")

    @ui.button(label="Krav-Maga", style=ButtonStyle.primary)
    async def handle_kravmaga(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(interaction, "Krav-Maga")

    @ui.button(label="Capoeira", style=ButtonStyle.primary)
    async def handle_capoeira(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(interaction, "Capoeira")

    @ui.button(label="Sambo", style=ButtonStyle.primary)
    async def handle_sambo(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(interaction, "Sambo")

    @ui.button(label="Kickboxing", style=ButtonStyle.primary)
    async def handle_kickboxing(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(interaction, "Kickboxing")

    @ui.button(label="MMA", style=ButtonStyle.primary)
    async def handle_mma(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(interaction, "MMA")
    
    @ui.button(label="Brazilian Jiu-Jitsu", style=ButtonStyle.primary)
    async def handle_bjj(self, interaction: discord.Interaction, button: ui.Button):
        await self.on_fighting_style_selected(interaction, "Brazilian Jiu-Jitsu")
