from .post_mortem import Death


def setup(bot):
    bot.add_cog(Death(bot))

