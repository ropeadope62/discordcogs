import json
from pathlib import Path

from .postmortem import PostMortem

with open(Path(__file__).parent / "info.json") as fp:
    __red_end_user_data_statement__ = json.load(fp)["end_user_data_statement"]


async def setup(bot):
    n = PostMortem(bot)
    await bot.add_cog(n)
