from sessionutils import Recap


async def setup(bot):
    await bot.add_cog(Recap(bot))
