import os
import discord
import PIL


class StoryMaps:
    async def show_map(self, ctx, location=None):
        """Show the current map location or list available locations."""
        if location == 'locations':
            await self.listmaps(ctx)
            return

        if location is None:
            await ctx.send("You need to enter a location. Try >storycraft showmap locations, for a full list of maps.")
            return
        # Use os.path.join to construct the file path
        map_image_path = os.path.join(
            os.path.dirname(__file__), "map_images", f"{location}.png"
        )
        if not os.path.exists(map_image_path):
            await ctx.send(f"Map for {location} not found.")
            print(f"Attempted to find map at: {map_image_path}")
            return
        with open(map_image_path, "rb") as f:
            picture = discord.File(f, filename=f"{location}.png")
        embed = discord.Embed(title=f"Map of {location}")
        embed.set_thumbnail(url="https://i.imgur.com/3FaAUZI.png")
        embed.set_image(url=f"attachment://{location}.png")
        await ctx.send(embed=embed, file=picture)

    async def listmaps(self, ctx):
        """List available map locations."""
        map_image_path = os.path.join(
            os.getcwd(), "story_maps", "map_images"
        )
        if not os.path.exists(map_image_path):
            await ctx.send("Map directory not found.")
            return
        map_files = [f.replace('.png', '') for f in os.listdir(map_image_path) if f.endswith('.png')]
        if not map_files:
            await ctx.send("No map files found.")
            return
        map_list = ', '.join(map_files)
        for map_item in map_list: 
            map_item = map_item.title()
        await ctx.send(f"Available maps: {map_list}")