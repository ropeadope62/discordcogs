import asyncio
from .spectre import Spectre 
async def setup(bot):
    await bot.add_cog(Spectre(bot))