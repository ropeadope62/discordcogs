

from ast import arguments
import discord
from redbot.core import commands

dictionary = {"je":"j'","tu":'es',"il": 'e', "elle":'e',"nous":'ons',"vous":'ez',"ils":'ent',"elles":'ent'}
global _
_ = dictionary

class french(commands.Cog):
    def __init__(self, bot):     
        self.bot = bot

    @commands.command()
    async def conjugate(self, ctx, arg: str):
        await ctx.send(""" Slurm's Fantastic French Conjugator is working!""")
        for key in dictionary:
            if arg.endswith('er'):
                b = arg[:-2]
            if key == 'je':
                c = (key, dictionary[key] + b + 'e')
                await ctx.send(c)
            else:
                d = (key,b + dictionary[key])
                await ctx.send(d)

