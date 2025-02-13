from discord import app_commands
from discord.ext import commands


class MySQLExample(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.store = []
    
    @commands.hybrid_command(name='settings', description='Edit settings')
    @app_commands.describe(value='a value')
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @commands.cooldown(5, 5, commands.BucketType.user)
    async def settings(self, ctx, *, value: str=None):
        user = ctx.author.id

        if not value:
            async with self.bot.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT setting FROM users WHERE id = %s", (user,))
                    row = await cur.fetchone()

            if not row:
                return await ctx.send("No settings found.")
                
            return await ctx.send(f'Settings: {row[0]}')
        
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO users (id, setting) VALUES (%s, %s) ON DUPLICATE KEY UPDATE setting = %s",
                    (user, value, value)
                )
            await conn.commit()
        
        await ctx.send(f'Settings updated to {value}.')
    

async def setup(bot: commands.Bot):
    await bot.add_cog(MySQLExample(bot))
