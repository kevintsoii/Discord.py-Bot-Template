from discord import app_commands
from discord.ext import commands

import util.embed as embed


class RedisExample(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name='math', description='Solve a math equation')
    @app_commands.describe(equation='equation')
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def math(self, ctx, *, equation: str):
        cache = await self.bot.redis.get(f'math:{equation}')
        if cache:
            return await ctx.send(embed=embed.default_embed(f'{equation} = {cache}'))
        
        url = 'https://api.mathjs.org/v4/'
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "expr": equation
        }

        async with self.bot.session.post(url, json=payload, headers=headers, timeout=10) as response:
            result = await response.json()

        if result["error"]:
            return await ctx.send(embed=embed.error_embed(result["error"]))
        
        await self.bot.redis.set(f'math:{equation}', result["result"], ex=60)

        await ctx.send(embed=embed.success_embed(f'{equation} = {result["result"]}'))
    

async def setup(bot: commands.Bot):
    await bot.add_cog(RedisExample(bot))
