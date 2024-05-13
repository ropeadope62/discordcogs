from redbot.core import commands
import discord
import speech_recognition as sr
import io
from pydub import AudioSegment

class ScrapTalk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename.endswith(".ogg"):
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
