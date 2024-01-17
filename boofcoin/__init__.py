from .boofcoin import BoofCoin


async def setup(bot):
    await bot.add_cog(BoofCoin(bot))
