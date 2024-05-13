from redbot.core import commands, Config
import discord
import speech_recognition as sr
import io
from pydub import AudioSegment
import logging 
import os

logger = logging.FileHandler(
    filename='~/home/slurms/scraptalk.log',
    encoding='utf-8',
    mode='w'
)
logger.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
)
logging.getLogger('scraptalk').addHandler(logger)

class ScrapTalk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=12345612462435762457345347747890, force_registration=True)
        self.config.register_global(channels=[])

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.attachments:
            logger.debug(f"Message has attachments: {message.attachments}")
            for attachment in message.attachments:
                if attachment.filename.lower().endswith((".ogg", ".mp3", ".wav", ".m4a")):
                    logger.debug(f"Attachment is an audio file: {attachment.filename}")
                    await self.transcribe_audio(message, attachment.url)
                    logger.debug(f'Transcribed audio file: {attachment.filename}')
                    
    

    async def transcribe_audio(self, message, url):
        logger.debug(f"Transcribing audio file: {url}")
        recognizer = sr.Recognizer()
        logger.debug(f"Recognizer initialized")
        audio_data = await self.download_audio(url)
        logger.debug(f"Audio data downloaded")
        try:
            logger.debug(f"Transcribing audio data")
            file_format = os.path.splitext(url)[1].lower()[1:]
            logger.debug(f'File format: {file_format}')
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format=file_format)
            logger.debug(f'Audio segment created')
            
            audio_segment.export("scraptalk_temp.wav", format="wav")
            logger.debug(f'Audio segment exported to file')
            with sr.AudioFile("scraptalk_temp.wav") as source:
                logger.debug(f'Audio file loaded')
                audio = recognizer.record(source)
                logger.debug(f'Audio file recorded')
                text = recognizer.recognize_google(audio)
                await message.channel.send(f"ScrapTalk Transcription: {text}")
        except Exception as e:
            await message.channel.send(f"An error occurred: {e}")

    async def download_audio(self, url):
        logger.debug(f'Downloading audio from URL: {url}')
        async with self.bot.session.get(url) as response:
            logger.debug(f'Audio downloaded')
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
