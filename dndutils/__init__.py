from .storycraft import StoryCraft


async def setup(bot):
    await bot.add_cog(StoryCraft(bot))
