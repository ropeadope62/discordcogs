"""
===================================
Mixology
===================================

Description:
-------------
AI assitend mixology bot that can help you make drinks and learn about new drinks.

Commands:
---------
1. <command1>: <description of command1>
2. <command2>: <description of command2>
... 

Events:
-------
1. <event1>: <description of event1>
2. <event2>: <description of event2>
...

Dependencies:
-------------
This cog depends on the following external libraries:
1. discord.py
2. <any other dependencies>

Author:
-------
Slurms Mackenzie / ropeadope62

Date:
-----
22/03/2024

Version:
--------
v1.0
"""
import aiohttp
from redbot.core import commands
import openai
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

class Mixology(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        
    async def mixology_request(self, user_input: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "system", "content": "You are a helpful mixologist..."}, {"role": "user", "content": user_input}],
        }
        async with self.session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data['choices'][0]['message']['content']  # Adjusted to correct path based on API response structure
            else:
                return "I couldn't fetch a response. Please try again later."
    async def cog_unload(self):
        await self.session.close()
        
    async def mixology_ideas(self, user_input: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful mixologist who can suggest cocktails based on specific ingredients."},
                {"role": "user", "content": user_input}
            ],
        }
        async with self.session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data['choices'][0]['message']['content'].strip()  # Adjusted to correct path based on API response structure and strip leading/trailing spaces
            else:
                return "I couldn't fetch a response. Please try again later."
    
    
    @commands.group()
    async def mixology(self, ctx):
        """Mixology: Another world class cog by Slurms Mackenzie/ropeadope62!\n\nThis cog is designed to help you make drinks and learn about new drinks. Use the commands below to get started!"""
        
        pass

    @mixology.command()
    async def cocktail(self, ctx, *, cocktail_name: str):
        """Get a cocktail recipe"""
        response = await self.mixology_request(f"Give me the recipe for a {cocktail_name} cocktail.")
        await ctx.send(response)
    
    @mixology.command()    
    async def ideas(self, ctx, *, ingredients: str):
        """Get cocktail ideas based on ingredients you have."""
        response = await self.mixology_ideas(f"Give me the recipe for a {ingredients} cocktail.")
        await ctx.send(response)
      