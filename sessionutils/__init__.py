from .sessionutils import Recap
import asyncio


async def setup(bot):
    await bot.add_cog(Recap(bot))
