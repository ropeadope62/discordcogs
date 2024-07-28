from .bullshido import Bullshido


async def setup(bot):
    cog = Bullshido(bot)
    await bot.add_cog(cog)