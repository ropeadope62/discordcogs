import discord
from redbot.core import commands, Config
import spotipy
import random
import asyncio
from datetime import datetime, time
from redbot.core.bot import Red

class TuneWeaver(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "channel_id": None,
            "last_genre": None,
            "last_tracks": [],
        }
        self.config.register_guild(**default_guild)
        self.spotify = None
        self.task = self.bot.loop.create_task(self.daily_tracks())

    def cog_unload(self):
        self.task.cancel()

    async def initialize(self):
        client_id = await self.bot.get_shared_api_tokens("spotipy")
        if client_id.get("client_id") is None or client_id.get("client_secret") is None:
            print("Missing Spotify API credentials. Please set them using [p]set api spotify client_id,<your_client_id> client_secret,<your_client_secret>")
        else:
            self.spotify = spotipy.Spotify(
                client_credentials_manager=spotipy.oauth2.SpotifyClientCredentials(
                    client_id=client_id["client_id"],
                    client_secret=client_id["client_secret"]
                )
            )

    async def daily_tracks(self):
        await self.bot.wait_until_ready()
        await self.initialize()
        while not self.bot.is_closed():
            now = datetime.utcnow()
            if now.hour == 0 and now.minute == 0:
                await self.post_daily_tracks()
            await asyncio.sleep(60)  # Check every minute

    @commands.hybrid_group(name="tuneweaverset", description="Set TuneWeaver settings.")
    async def tuneweaverset_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help()
        
    @commands.hybrid_group(name="tuneweaver", description="TuneWeaver commands.")
    async def tuneweaver_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="TuneWeaver",
                description="Expand your Musical Horizons.",
                color=discord.Color.red()
            )

            embed.set_thumbnail(url="")
            embed.add_field(
                name="About",
                value="Another action packed discord cog by Slurms Mackenzie/ropeadope62\n Use [p]bullshidoset for admin commands!",
                inline=True
            )
            embed.add_field(
                name="Repo",
                value="If you liked this, check out my other cogs! https://github.com/ropeadope62/discordcogs",
                inline=True
            )

    @tuneweaverset_group.command()
    @commands.is_owner()
    async def channel(self, ctx, channel: discord.TextChannel):
        """Set the channel for daily track posts."""
        await self.config.guild(ctx.guild).channel_id.set(channel.id)
        await ctx.send(f"TuneWeaver channel set to {channel.mention}")

    @tuneweaverset_group.command()
    @commands.is_owner()
    async def trigger_selection(self, ctx):
        """Manually trigger the daily track selection."""
        if self.spotify is None:
            await ctx.send("Spotify API is not initialized. Please set up the API credentials.")
            return
        await self.post_daily_tracks(ctx.guild)
        
    @tuneweaverset_group.command()
    @commands.is_owner()
    async def daily_pick_time(self, ctx, time):
        """Set the time for daily track selection."""
        await ctx.send(f"Daily track selection time set to {time}")
        
    @tuneweaver_group.command()
    async def show_daily_tracks(self, ctx):
        await ctx.send("Displaying today's tracks for genre:")
        
    @tuneweaver_group.command()
    async def genre_info(self, ctx, genre: str):
        await ctx.send(f"Displaying information for genre: {genre}")
        
    @tuneweaver_group.command()
    async def genre_sample(self, ctx, genre: str):
        await ctx.send(f"Displaying sample tracks for genre: {genre}")

    async def post_daily_tracks(self, channel):
        await channel.send("Posting daily tracks")

    async def get_random_genre(self):
        # Implementation for getting a random genre
        pass

    async def get_tracks_from_genre(self, ctx, genre: str):