from .realblackjack import RealBlackJack


async def setup(bot):
    await bot.add_cog(RealBlackJack(bot))
