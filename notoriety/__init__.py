from notoriety import Notoriety 
import asyncio

async def setup(bot):
    await bot.add_cog(Notoriety(bot))