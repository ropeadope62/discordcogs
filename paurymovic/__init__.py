import aiohttp
from redbot.core.bot import Red
from .paurymovic import PauryMovic
from redbot.core.data_manager import cog_data_path
import os


async def download_file(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(filename, "wb") as f:
                    f.write(await resp.read())


async def setup(bot):
    cog = PauryMovic(bot)
    await bot.add_cog(cog)

    cog_folder = str(cog_data_path(cog))

    files = {
        "https://i.postimg.cc/pTP54jpF/you_are_the_father.png": os.path.join(
            cog_folder, "you_are_the_father.png"
        ),
        "https://i.postimg.cc/pTP54jpF/you_arenot_thefather.png": os.path.join(
            cog_folder, "you_arenot_thefather.png"
        ),
    }

    for url, file_path in files.items():
        if not os.path.exists(file_path):
            await download_file(url, file_path)
