from discord import app_commands
from discord.ext import commands

from util import load_file, save_file


STORE_FILE = 'db/store.json'


class FilesExample(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.store = []

    async def cog_load(self):
        self.store = await load_file(STORE_FILE)
    
    @commands.hybrid_command(name='store', description='Store values')
    @app_commands.describe(value='a value')
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @commands.cooldown(5, 5, commands.BucketType.user)
    async def store(self, ctx, *, value: str=None):
        if not value:
            return await ctx.send(f'Stored: {self.store}')
        
        self.store.append(value)
        await save_file(STORE_FILE, self.store)

        await ctx.send(f'Stored value: {value}')
    

async def setup(bot: commands.Bot):
    await bot.add_cog(FilesExample(bot))
