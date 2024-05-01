from .powerballs import Powerballs

async def setup(bot):
    cog = Powerballs(bot)
    await bot.add_cog(cog)

