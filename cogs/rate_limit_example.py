from discord.ext import commands

import util.embed as embed
from util import rate_limit


class RateLimitExample(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='slow')
    @rate_limit(2, 60, user=True, command=True)
    async def slow_command(self, ctx):
        """Test command with 2 uses per minute rate limit."""
        await ctx.send(embed=embed.success_embed('Slow - Success'))

    @commands.command(name='fast')
    @rate_limit(2, 10, user=True, command=True)
    async def fast_command(self, ctx):
        """Test command with 2 uses per 10 seconds rate limit."""
        await ctx.send(embed=embed.success_embed('Fast - Success'))

async def setup(bot: commands.Bot):
    await bot.add_cog(RateLimitExample(bot))

