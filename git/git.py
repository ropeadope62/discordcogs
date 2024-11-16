import discord
from redbot.core import commands
from discord.ext import tasks
import aiohttp

class ScrapGit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.get_cog("Config")
        self.session = aiohttp.ClientSession()
        self.commit_check_loop.start()

    def cog_unload(self):
        self.commit_check_loop.cancel()
        self.bot.loop.create_task(self.session.close())

    # Background commit checking loop
    @tasks.loop(minutes=30.0)
    async def commit_check_loop(self):
        async for guild_id, guild_data in self.config.all_guilds().items():
            if not guild_data["api_key"]:
                continue
            for repo_name, repo_data in guild_data["watchlist"].items():
                if not repo_data["enabled"]:
                    continue
                try:
                    commits = await self.fetch_commits(guild_data["api_key"], repo_name)
                    if commits:
                        for commit in commits:
                            await self.post_commit(guild_id, repo_name, commit)
                except Exception as e:
                    print(f"Error checking {repo_name} in {guild_id}: {e}")

    # GitHub API requests
    async def fetch_commits(self, api_key, repo_name):
        url = f"https://api.github.com/repos/{repo_name}/commits"
        headers = {"Authorization": f"token {api_key}"}
        async with self.session.get(url, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()

    # Post commit notification
    async def post_commit(self, guild_id, repo_name, commit_data):
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return
        channel_id = await self.config.guild(guild).notification_channel()
        channel = guild.get_channel(channel_id)
        if not channel:
            return
        try:
            embed = discord.Embed(title="New Commit",
                                  description=commit_data["commit"]["message"],
                                  color=discord.Color.green())
            embed.set_author(name=commit_data["commit"]["author"]["name"],
                             icon_url=commit_data["author"]["avatar_url"])
            embed.add_field(name="Repository",
                            value=f"[{repo_name}](https://github.com/{repo_name})")
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending commit notification for {repo_name} in {guild_id}: {e}")

    # Commands
    @commands.group()
    async def git(self, ctx):
        """GitHub integration commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(self.github)

    @git.command()
    @commands.has_permissions(administrator=True)
    async def setapikey(self, ctx, api_key: str):
        """Set the GitHub API key for accessing the API."""
        # Validation and error handling
        ...

    @git.command()
    async def addrepo(self, ctx, repository: commands.clean_content):
        """Add a GitHub repo to the watchlist."""
        watchlist = await self.config.guild(ctx.guild).watchlist()
        if repository in watchlist:
            await ctx.send(f"{repository} is already in the watchlist.")
        else:
            watchlist[repository] = {"enabled": True}
            await ctx.send(f"Added {repository} to the watchlist.")

    @git.command()
    async def removerepo(self, ctx, repository: commands.clean_content):
        """Remove a repo from the watchlist."""
        watchlist = await self.config.guild(ctx.guild).watchlist()
        if repository in watchlist:
            del watchlist[repository]
            await ctx.send(f"Removed {repository} from the watchlist.")
        else:
            await ctx.send(f"{repository} is not in the watchlist.")

    @git.command()
    async def watchlist(self, ctx):
        """View the current GitHub watchlist."""
        watchlist = await self.config.guild(ctx.guild).watchlist()
        if not watchlist:
            await ctx.send("The watchlist is empty.")
            return
        embeds = []
        for repo_name, repo_data in watchlist.items():
            enabled = repo_data["enabled"]
            embed = discord.Embed(title=repo_name,
                                  description="Enabled" if enabled else "Disabled")
            embeds.append(embed)
        paginator = commands.Paginator(embeds=embeds)
        try:
            await paginator.start(ctx)
        except Exception as e:
            print(f"Error starting paginator for watchlist in {ctx.guild.id}: {e}")