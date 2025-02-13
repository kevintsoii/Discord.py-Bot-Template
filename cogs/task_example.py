from discord import app_commands
from discord.ext import commands, tasks


class TaskExample(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.top_100 = []
    
    async def cog_load(self):
        self.update_top.start()
    
    def cog_unload(self):
        self.update_top.cancel()

    @tasks.loop(seconds=10*60)
    async def update_top(self):
        async with self.bot.session.get(f'https://min-api.cryptocompare.com/data/top/mktcapfull?limit=100&tsym=USD') as response:
            result = await response.json()

        top_100 = []
        for coin in result["Data"]:
            top_100.append(coin["CoinInfo"]["FullName"])
        self.top_100 = top_100
        
    @commands.hybrid_command(name='top', description='List the top 100 cryptocurrencies')
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def top(self, ctx):
        await ctx.send(", ".join(self.top_100))
    

async def setup(bot: commands.Bot):
    await bot.add_cog(TaskExample(bot))
