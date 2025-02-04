from .cog import DayByDayCog

def setup(bot):
    bot.add_cog(DayByDayCog(bot))