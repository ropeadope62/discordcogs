from .flashdelete import FlashDelete
import asyncio


async def setup(bot):
    await bot.add_cog(FlashDelete(bot))
