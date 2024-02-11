import asyncio
from .spectre import Spectre 
def setup(bot):
    bot.add_cog(Spectre(bot))