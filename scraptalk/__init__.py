from .scraptalk import ScrapTalk


async def setup(bot):
    await bot.add_cog(ScrapTalk(bot))
