import discord
from redbot.core import commands
from redbot.core.data_manager import cog_data_path
import random
from datetime import timedelta, datetime
from typing import List
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap
import os


class PauryMovic(commands.Cog):
    """**Welcome to Broad Street Labs:tm: - PauryMovic DNA Test:registered:**"""

    __author__ = ["ropeadpope62"]
    __version__ = "0.1.0"

    results: List[str] = [
        "you ARE the father!",
        "you are NOT the father!",
    ]

    def __init__(self, bot):
        self.bot = bot

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """
        Thanks for using Broadstreet Labs DNA Test!
        """
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}"

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def paurymovic(
        self, ctx: commands.Context, user1: discord.Member, user2: discord.Member
    ):
        """
        The Paury Movic test will determine if the first user is the father of the second user.

        Example: `>paurymovic @user1 @user2`
        """
        try:
            if user1 is None or user2 is None:
                help_menu = (
                    "**Paury Movic Help Menu**\n"
                    "To use the command, mention two users.\n"
                    "Example: `>paurymovic @user1 @user2`\n\n"
                    "This test will determine if @user1 is the father of @user2.\n"
                )
                await ctx.send(help_menu)
                return

            img_path_father = os.path.join(
                str(cog_data_path(self)), "you_are_the_father.png"
            )
            print(img_path_father)
            img_path_not_father = os.path.join(
                str(cog_data_path(self)), "you_arenot_thefather.png"
            )
            print(img_path_not_father)
            img_path_result = os.path.join(str(cog_data_path(self)), "pm_result.png")
            print(img_path_result)
            font_path = os.path.join(str(cog_data_path(self)), "GothamBold.ttf")
            print(font_path)
            account_age_difference = user1.created_at - user2.created_at

            if account_age_difference < timedelta(days=2 * 365):  # 8 years difference
                test_result = self.results[1]
                img_url = img_path_not_father
            else:
                test_result = self.results[0]
                img_url = img_path_father

            # Fetch the template image
            print(img_path_father)
            print(img_path_not_father)
            print(img_path_result)
            print(f"Image Path: {img_url}")
            print(f"Image Extension: {os.path.splitext(img_url)[1]}")
            img = Image.open(img_url)

            draw = ImageDraw.Draw(img)
            await ctx.send(draw)
            font = ImageFont.truetype(font_path, 24)
            print(font)
            text = f"The results are in.. {user1.display_name}, when it comes to {user2.display_name}, {test_result}"
            wrapper = textwrap.TextWrapper(
                width=22
            )  # Replace 40 with the actual maximum width
            lines = wrapper.wrap(text=text)
            y_text = 450
            for line in lines:
                draw.text(
                    (425, y_text),
                    line,
                    fill=(58, 40, 100),
                    font=font,
                )
                y_text += 30
            img.save(img_path_result)

            await ctx.send(file=discord.File(img_path_result, filename="pm_result.png"))

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @paurymovic.error
    async def paurymovic_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                "Please wait for 1 minute before submitting another DNA test."
            )
        else:
            await ctx.send(f"An error occurred: {str(error)}")
