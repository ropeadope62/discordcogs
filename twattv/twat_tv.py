import discord
from discord.ext import commands, Embed
import datetime

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class TwatTV(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.events = []  # In-memory storage for simplicity

    @commands.group(name="twattv")
    async def twattv_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @twattv_group.command(name="schedule")
    async def view_schedule(self, ctx):
        if not self.events:
            await ctx.send("No events scheduled.")
            return
        schedule = "\n".join([f"{event['time']} - {event['name']}" for event in self.events])
        await ctx.send(f"Streaming Schedule:\n{schedule}")

    @twattv_group.command(name="host")
    async def host_stream(self, ctx, time: str, *, name: str):
        try:
            event_time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M")
        except ValueError:
            await ctx.send("Invalid time format. Use YYYY-MM-DD HH:MM")
            return
        self.events.append({"time": event_time, "name": name})
        self.events.sort(key=lambda x: x['time'])
        await ctx.send(f"Scheduled '{name}' on {event_time}")
        
    @twattv_group.command(name="next")
    async def next_stream(self, ctx):
        if not self.events:
            await ctx.send("No events scheduled.")
            return
        next_event = self.events[0]
        await ctx.send(f"Next stream: {next_event['name']} at {next_event['time']}")
        
    @twattv_group.command(name="cancel")
    async def cancel_stream(self, ctx, time: str):
        try:
            event_time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M")
        except ValueError:
            await ctx.send("Invalid time format. Use YYYY-MM-DD HH:MM")
            return
        for i, event in enumerate(self.events):
            if event['time'] == event_time:
                del self.events[i]
                await ctx.send(f"Canceled '{event['name']}' on {event_time}")
                return
        await ctx.send("No matching event found.")
    
    @twattv_group.command(name="about")
    async def about(self, ctx):
        embed = Embed(title="About twattv", description="Twat.tv is the official Streaming platform of The Sanctuary Discord Server, bringing you the best game streaming content from our very own members. \n The best part about Twat.tv is that it is fully managed by our members, who can create or manage their own events directly into the server schedule. \n Have something you want to stream? Do it! The Twat.tv commands, accessible with -twattv have everything you need for scheduling, displaying or managing upcoming live events.", color=0x6441A5)
        embed.set_image(url="https://i.ibb.co/Yp2XGpz/ef0c3d6bbb62b0e6a9a01482bc02b366.png")
        await ctx.send(embed=embed)
        

    

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")