from .main import Fishing


async def setup(bot):
    await bot.add_cog(Fishing(bot))
