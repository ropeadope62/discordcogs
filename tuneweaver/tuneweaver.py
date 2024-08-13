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
        self.config = Config.get_conf(self, identifier=1234567891274843525235889345210)
        default_guild = {
            "daily_weave_time": None,
            "channel_id": None,
            "last_genre": None,
            "last_tracks": [],
        }
        self.config.register_guild(**default_guild)
        self.spotify = None
        self.task = self.bot.loop.create_task(self.daily_weave_loop())
        self.imagestore = "/home/slurms/ScrapGPT/scrapgpt_data/cogs/TuneWeaver/images/"


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
    async def get_random_genre(self, ctx):
        if self.spotify is None:
            raise ValueError("Spotify API is not initialized. Please set up the API credentials.")
        
        try: 
            # Get a list of genres
            genres = self.spotify.recommendation_genre_seeds()
            last_genre = await self.config.guild(ctx.guild).last_genre()
            genre = random.choice(genres["genres"])
            # If the genre is the same as the last genre, pick a new one
            while genre == last_genre:
                genre = random.choice(genres["genres"])
                
            # update the last genre in the guild config
            await self.config.guild(ctx.guild).last_genre.set(genre)
            return genre
        
        except Exception as e:
            print(e)
            return None

    async def daily_weave_loop(self):
        await self.bot.wait_until_ready()
        await self.initialize()
        while not self.bot.is_closed():
            now = datetime.now()
            for guild in self.bot.guilds: 
                weave_time_str = await self.config.guild(guild).daily_weave_time()
                weave_time = datetime.strptime(weave_time_str, "%H:%M").time()
                if now.time().hour == weave_time.hour and now.time().minute == weave_time.minute:
                    await self.post_daily_weave(guild)
            await asyncio.sleep(60)
            
    async def post_daily_weave(self, ctx, guild):
        channel_id = await self.config.guild(guild).channel_id()
        if not channel_id:
            return
        channel = guild.get_channel(channel_id)
        if not channel:
            return

        genre = await self.get_random_genre(ctx)
        if not genre: 
            await channel.send("Failed to retrieve a random genre. Please try again later")
            return
        
        tracks = await self.weave_tracks_from_genre(genre)
        if not tracks: 
            await channel.send("Failed to retrieve tracks for the genre. Please try again later")
            return
        
        embed = discord.Embed(title=f"TrackWeaver - Daily Weave for today's genre: {genre}", color=discord.Color.purple())
        for i, track in enumerate(tracks, 1):
            duration = f"{track['duration_ms'] // 60000}:{(track['duration_ms'] % 60000) // 1000:02d}"
            embed.add_field(
                name=f"Track {i}: {track['name']}",
                value=f"By: {track['artists']}\n"
                      f"Album: {track['album']}\n"
                      f"Duration: {duration}\n"
                      f"Popularity: {track['popularity']}/100\n"
                      f"[Listen on Spotify]({track['url']})\n"
                      f"[Preview]({track['preview_url']})",
                inline=False
            )
            
        await channel.send(embed=embed)
        
    async def weave_tracks_from_genre(self, genre, limit=5):
        if self.spotify is None:
            raise ValueError("Spotify API is not initialized. Please set up the API credentials.")
        try:
            results = self.spotify.recommendations(
                seed_genres=[genre],
                limit=limit,
                market="US",
                min_popularity=50
            )
            
            tracks = []
            for track in results["tracks"]:
                artists = ", ".join([artist["name"] for artist in track["artists"]])
                album = track["album"]["name"]
                preview_url = track["preview_url"]
                tracks.append({
                    'name': track['name'],
                    'artists': artists,
                    'album': album,
                    'url': track['external_urls']['spotify'],
                    'preview_url': preview_url,
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity']
                })
                
            # In instances where he recommendations are less than the limit, we can search for more tracks
            if len(tracks) < limit:
                more_results = self.spotify.search(q=f'genre:"{genre}"', type='track', limit=limit-len(tracks))
                for track in more_results['tracks']['items']:
                    artists = ", ".join([artist['name'] for artist in track['artists']])
                    album = track['album']['name']
                    preview_url = track.get('preview_url', 'No preview available')
                    tracks.append({
                        'name': track['name'],
                        'artists': artists,
                        'album': album,
                        'url': track['external_urls']['spotify'],
                        'preview_url': preview_url,
                        'duration_ms': track['duration_ms'],
                        'popularity': track['popularity']
                    })
                    
            random.shuffle(tracks)
            return tracks[":limit"]
        
        except spotipy.SpotifyException as e:
            print(f"Spotify API error: {str(e)}")
            return None
        except Exception as e:
            print(f"Error fetching tracks: {str(e)}")
            return None

    @commands.hybrid_group(name="tuneweaverset", description="Set TuneWeaver settings.")
    async def tuneweaverset_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="TuneWeaver",
                description="Expand your Musical Horizons.",
                color=discord.Color.purple()
            )

            embed.set_thumbnail(url="https://i.ibb.co/tzxqWJ8/tuneweaver-logo-circle.png")
            embed.add_field(
                name="About",
                value="A discord cog by Slurms Mackenzie/ropeadope62\n Use /tuneweaverset for admin commands.",
                inline=True
            )
            embed.add_field(
                name="Repo",
                value="If you liked this cog, check out my other cogs! https://github.com/ropeadope62/discordcogs",
                inline=True
            )
            await ctx.send(embed=embed)
            
    @commands.hybrid_group(name="tuneweaver", description="TuneWeaver commands.")
    async def tuneweaver_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="TuneWeaver",
                description="Expand your Musical Horizons.",
                color=discord.Color.purple()
            )

            embed.set_thumbnail(url="https://i.ibb.co/tzxqWJ8/tuneweaver-logo-circle.png")
            embed.add_field(
                name="About",
                value="A discord cog by Slurms Mackenzie/ropeadope62\n Use /tuneweaverset for admin commands.",
                inline=True
            )
            embed.add_field(
                name="Repo",
                value="If you liked this cog, check out my other cogs! https://github.com/ropeadope62/discordcogs",
                inline=True
            )
            await ctx.send(embed=embed)

    @tuneweaverset_group.command()
    @commands.is_owner()
    async def channel(self, ctx, channel: discord.TextChannel):
        """Set the channel for daily track posts."""
        await self.config.guild(ctx.guild).channel_id.set(channel.id)
        await ctx.send(f"TuneWeaver channel set to {channel.mention}")

    @tuneweaverset_group.command(name="weave", description="Manually trigger the daily track selection.")
    @commands.is_owner()
    async def trigger_weave(self, ctx):
        """Manually trigger the daily track selection."""
        if self.spotify is None:
            await ctx.send("Spotify API is not initialized. Please set up the API credentials.")
            return
        await self.post_daily_weave(ctx, ctx.guild)
        
    @tuneweaverset_group.command(name="dailyweavetime", description="Set the time for daily track selection.")
    @commands.is_owner()
    async def daily_weave_time(self, ctx, weave_time: str):
        """Set the time for daily track selection."""
        """Set the time for daily track posts (in HH:MM format, UTC)."""
        try:
            datetime.strptime(weave_time, "%H:%M")
            await self.config.guild(ctx.guild).post_time.set(weave_time)
            await ctx.send(f"TuneWeaver daily weave time set to {weave_time} UTC")
        except ValueError:
            await ctx.send("Invalid time format. Please use HH:MM (24-hour format).")

        
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

    @tuneweaver_group.command(name="randomgenre")
    async def randomgenre(self, ctx):
        """ Get a random genre """
        try: 
            genre = await self.get_random_genre(ctx)
            if genre: 
                await ctx.send(f"Random genre: {genre}")
            else: 
                await ctx.send("Failed to retrieve a random genre.")
        except Exception as e:
            print(e)
            await ctx.send("Failed to retrieve a random genre.")

    #async def get_tracks_from_genre(self, ctx, genre: str):
    
    