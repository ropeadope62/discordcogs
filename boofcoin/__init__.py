from .boofcoin import Boofcoin


def setup(bot):
    bot.add_cog(Crypto(bot))
