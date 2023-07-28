from .aichat import AIChatSomething


async def setup(bot):
    cog = AIChatSomething(bot)
    await bot.add_cog(cog)
