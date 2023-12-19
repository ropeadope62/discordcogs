import asyncio
from .russianroulette import RussianRoulette

async def setup(bot):
    await bot.add_cog(RussianRoulette(bot))