from redbot.core import commands, Config
import discord
import speech_recognition as sr
import io
from pydub import AudioSegment

class ScrapTalk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=12345612462435762457345347747890, force_registration=True)
        self.config.register_global(channels=[])

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename.lower().endswith((".ogg", ".mp3", ".wav", ".m4a")):
                    await self.transcribe_audio(message, attachment.url)
                    
    

    async def transcribe_audio(self, message, url):
        recognizer = sr.Recognizer()
        audio_data = await self.download_audio(url)
        try:
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="ogg")
            audio_segment.export("scraptalk_temp.wav", format="wav")
            with sr.AudioFile("scraptalk_temp.wav") as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
                await message.channel.send(f"ScrapTalk Transcription: {text}")
        except Exception as e:
            await message.channel.send(f"An error occurred: {e}")

    async def download_audio(self, url):
        async with self.bot.session.get(url) as response:
            return await response.read()

    @commands.group()
    async def scraptalk(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @scraptalk.command(name="channels", alias="addchannels", description="Adds channels to the list of channels to transcribe.")
    async def add_transcription_channel(self, ctx, channel: discord.TextChannel):
        async with self.config.channels() as channels:
            if channel.id not in channels:
                channels.append(channel.id)
                await ctx.send(f"{channel.name} added to transcription channels.")
            else:
                await ctx.send(f"{channel.name} is already a transcription channel.")
                
    @scraptalk.command(name="removechannels", alias="removechannels", description="Removes channels from the list of channels to transcribe.")
    async def remove_transcription_channel(self, ctx, channel: discord.TextChannel):
        async with self.config.channels() as channels:
            if channel.id in channels:
                channels.remove(channel.id)
                await ctx.send(f"{channel.name} removed from transcription channels.")
            else:
                await ctx.send(f"{channel.name} was not a transcription channel.")
