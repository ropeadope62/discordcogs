from .acrocat import AcroCat


async def setup(bot):
    await bot.add_cog(AcroCat(bot))
