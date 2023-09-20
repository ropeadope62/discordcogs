from .frenchconjugator import french 


def setup(bot):
    await bot.add_cog(french(bot))

