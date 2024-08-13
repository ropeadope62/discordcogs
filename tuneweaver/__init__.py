from .tuneweaver import TuneWeaver


async def setup(bot):
    cog = TuneWeaver(bot)
    await bot.add_cog(cog)