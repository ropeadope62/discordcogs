import os
from redbot.core import commands
import azure.cognitiveservices.speech as speechsdk

class ScrapTTS(commands.Cog):
    """Text-to-Speech Cog using Azure TTS"""

    def __init__(self, bot):
        self.bot = bot
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv('SPEECH_KEY'),
            region=os.getenv('SPEECH_REGION')
        )
        self.speech_config.speech_synthesis_voice_name = 'en-US-AriaNeural'
        self.audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    @commands.command()
    async def speak(self, ctx, *, text: str):
        """Speak the text using Azure TTS."""
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, 
            audio_config=self.audio_config
        )
        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            await ctx.send(f"Speech synthesized for text: {text}")
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            await ctx.send(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    await ctx.send(f"Error details: {cancellation_details.error_details}")

def setup(bot):
    bot.add_cog(ScrapTTS(bot))