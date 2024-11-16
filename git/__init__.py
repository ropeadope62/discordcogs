from .git import ScrapGit
import asyncio


async def setup(bot):
    await bot.add_cog(ScrapGit(bot))
