from .boofcoin import BoofCoin


def setup(bot):
    bot.add_cog(BoofCoin(bot))
