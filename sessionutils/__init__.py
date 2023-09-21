from recap import Recap
from .recap_ai import OpenAI


async def setup(bot):
    await bot.add_cog(Recap(bot))
    await bot.add_cog(OpenAI(bot))
