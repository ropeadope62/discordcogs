from .roll_off import RollOff


async def setup(bot):
    await bot.add_cog(RollOff(bot))
