from .scraptts import ScrapTTS


async def setup(bot):
    await bot.add_cog(ScrapTTS(bot))
