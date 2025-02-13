import random

from discord.ext import commands


class PrefixExample(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='coinflip', aliases=['cf'], description='Flip a coin')
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def coinflip(self, ctx):
        await ctx.send(random.choice(['Heads', 'Tails']))
    
    @commands.command(name='error', aliases=['err'], description='Raise a test error')
    async def error(self, ctx):
        raise Exception('Test Error')

async def setup(bot: commands.Bot):
    await bot.add_cog(PrefixExample(bot))
