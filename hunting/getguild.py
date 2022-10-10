from discord import *
from discord.ext import *
client = Discord.Client();

client.on('ready', () => {
        client.guilds.forEach(guild => console.log(guild.id, guild.name))
        };