import discord
from discord.ext import commands
import json 
from redbot.core import commands
import asyncio 


class Spectre(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_cache = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.invite_cache[guild.id] = await guild.invites()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        invites_before_join = self.invite_cache.get(guild.id)
        invites_after_join = await guild.invites()
        invite = None

        for invite_before in invites_before_join:
            for invite_after in invites_after_join:
                if invite_before.code == invite_after.code and invite_before.uses < invite_after.uses:
                    invite = invite_before
                    break

        if invite:
            inviter = invite.inviter
            channel = self.bot.get_channel(1202968017785585705)  # Replace with your channel ID
            await channel.send(f"{member.display_name} JOINED WITH {invite.code}. THE INVITE WAS CREATED BY {inviter.display_name}")

        invite_data = {
            "member": member.display_name,
            "invite_code": invite.code,
            "inviter": inviter.display_name
        }
        with open('spectre_data.json', 'w') as json_file:
            json.dump(invite_data, json_file)

async def setup(bot):
    await bot.add_cog(Spectre(bot))