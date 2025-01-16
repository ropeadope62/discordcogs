from .captioncrunch import CaptionCrunch


async def setup(bot):
    await bot.add_cog(CaptionCrunch(bot))