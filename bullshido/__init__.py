from .bullshido import Bullshido


async def setup(bot):
    cog = Bullshido(bot)
    await bot.add_cog(cog)
    await bot.loop.create_task(cog.update_task())