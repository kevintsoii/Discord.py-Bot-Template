import os

import discord
from dotenv import load_dotenv
from async_lru import alru_cache
from discord import app_commands
from discord.ext import commands
from dateutil.parser import isoparse


load_dotenv()


class AlruExample(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.EXAMPLE_API_KEY = os.getenv("EXAMPLE_API_KEY", None)

    def parse_time(self, time: str):
        return int(isoparse(time).timestamp())
    
    @alru_cache(maxsize=32, ttl=10*60)
    async def fetch_github_profile(self, username: str):
        url = f'https://api.github.com/users/{username}'
        async with self.bot.session.get(url, timeout=5) as resp:
            user_info = await resp.json()
            
        self.bot.logger.debug(user_info)
        
        if 'message' in user_info:
            return None
        return user_info

    @commands.hybrid_command(name='github', description='View a GitHub profile')
    @app_commands.describe(username='GitHub username')
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def github(self, ctx, *, username: str):
        user_info = await self.fetch_github_profile(username)

        embed=discord.Embed(
            color=0,
            title=f'{user_info["login"]}',
            description=f'{user_info["name"] if user_info["name"] and user_info["name"] != user_info["login"] else ""}',
            url=f'{user_info["html_url"]}'
        )

        embed.add_field(name='Followers', value=f'{user_info["followers"]:,}', inline=True)
        embed.add_field(name='Following', value=f'{user_info["following"]:,}', inline=True)
        embed.add_field(name='Repos', value=f'{user_info["public_repos"]:,}', inline=True)

        embed.add_field(name='Joined', value=f'<t:{self.parse_time(user_info["created_at"])}:D>', inline=True)
        embed.add_field(name='Updated', value=f'<t:{self.parse_time(user_info["updated_at"])}:D>', inline=True)
        embed.add_field(name='ID', value=f'{user_info["id"]:,}', inline=True)
        
        if user_info["bio"]: embed.add_field(name='Bio', value=user_info["bio"], inline=False)

        embed.set_thumbnail(url=user_info["avatar_url"])

        await ctx.send(embed=embed)
    

async def setup(bot: commands.Bot):
    await bot.add_cog(AlruExample(bot))
