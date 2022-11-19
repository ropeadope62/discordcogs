from .boofcoin import BoofCoin


def setup(bot):
    bot.add_cog(Crypto(bot))
