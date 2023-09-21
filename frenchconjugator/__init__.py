import asyncio
from .frenchconjugator import french 


asyc def setup(bot):
    await bot.add_cog(french(bot))

