from redbot.core import commands, Config
from .ui_elements import SelectFightingStyleView
from .fighting_game import FightingGame
import discord 

class Bullshido(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=123123451514345671215451351235890)
        default_user = {
            "fighting_style": None,
            "wins": 0,
            "losses": 0,
            "level": 1,
            "training_level": 1,
            "nutrition_level": 1,
            "morale": 100,
            "intimidation_level": 0
        }
        self.config.register_user(**default_user)
        
    async def set_fighting_style(self, user, style):
        await self.config.user(user).fighting_style.set(style)
        await user.send(f"Your fighting style has been set to {style}.")
        
    bullshido_group = commands.slash_command_group("bullshido", "Commands related to the Bullshido game")
    
    @bullshido_group.command(name="info")
    async def bullshido_info(self, interaction: discord.Interaction):
        """Displays information about the Bullshido game commands."""
        embed = discord.Embed(title="Bullshido Game Commands", description="Learn how to play and interact with the Bullshido game.", color=0x00ff00)
        embed.add_field(name="/bullshido select_fighting_style", value="Select your fighting style.", inline=False)
        embed.add_field(name="/bullshido list_fighting_styles", value="List all available fighting styles.", inline=False)
        embed.set_image(url="https://i.ibb.co/GWpXztm/bullshido.png")  
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bullshido_group.command(name="select_fighting_style")
    async def select_fighting_style(self, interaction: discord.Interaction):
        """Select your fighting style."""
        view = SelectFightingStyleView(self.set_fighting_style, interaction.user)
        await interaction.response.send_message("Please select your fighting style:", view=view, ephemeral=True)

    @bullshido_group.command(name="list_fighting_styles")
    async def list_fighting_styles(self, interaction: discord.Interaction):
        """List all available fighting styles."""
        styles = ["Karate", "Muay-Thai", "Aikido", "Boxing", "Kung-Fu", "Judo", "Taekwondo", "Wrestling", "Sambo", "MMA", "Capoeira", "Kick-Boxing", "Krav-Maga"]
        await interaction.response.send_message(f"Available fighting styles: {', '.join(styles)}", ephemeral=True)
    
    @bullshido_group.command(name="start_fight")
    async def start_fight(self, interaction: discord.Interaction, opponent: discord.Member):
        """Start a fight with another player."""
        player1 = interaction.user
        player2 = opponent
        
        player1_data = await self.config.user(player1).all()
        player2_data = await self.config.user(player2).all()
        
        if not player1_data['fighting_style'] or not player2_data['fighting_style']:
            await interaction.response.send_message("Both players must have selected a fighting style before starting a fight.", ephemeral=True)
            return
        
        game = FightingGame(player1, player2, player1_data, player2_data)
        result = game.start_game()
        
        await interaction.response.send_message(result, ephemeral=True)

    async def get_player_data(self, user):
        fighting_style = await self.config.user(user).fighting_style()
        wins = await self.config.user(user).wins()
        losses = await self.config.user(user).losses()
        return {"fighting_style": fighting_style, "wins": wins, "losses": losses}
    
    async def update_player_stats(self, user, win=True):
        if win:
            await self.config.user(user).wins.set(await self.config.user(user).wins() + 1)
        else:
            await self.config.user(user).losses.set(await self.config.user(user).losses() + 1)
