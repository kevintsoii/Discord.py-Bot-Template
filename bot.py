import os
import sys
import asyncio
import logging
import importlib
import traceback

import aiohttp
import discord
import aiomysql
from dotenv import load_dotenv
import redis.asyncio as aioredis
from discord import app_commands
from discord.ext import commands

import config
import util.embed as embed
from util import logger, MetricsHandler


load_dotenv()


def convert_seconds(seconds: int):
    seconds = int(seconds)
    if (minutes := seconds // 60) > 1:
        return f'{minutes} minutes and {seconds % 60} seconds'
    return f'{seconds} seconds'

def fetch_cogs():
    cogs = []
    for root, _, files in os.walk('./cogs'):
        root = os.path.normpath(root)
        for file in files:
            if file.endswith('.py'):
                cog_path = os.path.join(root, file).replace(os.sep, '.')[:-3]
                if cog_path.startswith('cogs.'):
                    cogs.append(cog_path)
    return cogs

class Bot(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.default()
        if config.message_intent:
            intents.message_content = True

        super().__init__(
            command_prefix=commands.when_mentioned_or(config.prefix),
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions.none(),
            owner_ids=config.owners,
            intents=intents,
            help_command=None,
            status=discord.Status.online,
            activity=discord.CustomActivity(name=config.activity)
        )

        self.logger = logger
        self.metrics_handler = MetricsHandler()

    async def setup_hook(self):
        if "--development" not in sys.argv:
            await asyncio.to_thread(self.metrics_handler.start_server)

            self.pool = await aiomysql.create_pool(
                host="mysql",
                port=3306,
                user="admin",
                password="password",
                db="discord_bot",
            )

            self.redis = await aioredis.Redis(host='redis', port=6379, decode_responses=True)

        self.session = aiohttp.ClientSession()

        cog_paths = fetch_cogs()
        cog_paths.sort(key=lambda cog: (cog == "cogs.crypto.price", cog))
        for cog in cog_paths:
            try: 
                await self.load_extension(cog)
            except Exception as e:
                self.logger.critical(f'ERROR: {cog} => {e}')

    async def on_ready(self):
        await self.tree.sync()
        self.logger.info(f'{self.user} is now ready.')
    
    async def on_command(self, ctx):
        user = getattr(ctx.author, "id", "Unknown")
        command_name = getattr(ctx.command, "name", "Unknown")
        cog_name = getattr(ctx.cog, "qualified_name", "Unknown")

        self.logger.debug(f'{user} - {cog_name}.{command_name} - {ctx.message.content}')

        self.metrics_handler.command_counter.labels(
            cog=cog_name,
            command=command_name,
        ).inc()

    async def on_command_error(self, ctx, error):
        if isinstance(error, (commands.CommandNotFound, commands.MissingRequiredArgument, commands.BadArgument)):
            pass
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(
                embed=embed.error_embed('You do not have permission to use this command!'),
                ephemeral=True
            )
        elif isinstance(error, (commands.CommandOnCooldown, app_commands.CommandOnCooldown)):
            if ctx.message.author.id in config.owners:
                return await ctx.reinvoke()

            await ctx.send(
                embed=embed.error_embed(f'You are on cooldown. Try again in {convert_seconds(int(error.retry_after))}.'),
                ephemeral=True
            )

            self.logger.warning(f'{ctx.author.id} ratelimited')
        else:
            tb = traceback.extract_tb(getattr(error, 'original', error).__traceback__)
            user = getattr(ctx.author, "id", "Unknown")
            command_name = getattr(ctx.command, "name", "Unknown")
            cog_name = getattr(ctx.cog, "qualified_name", "Unknown")
            error_type = f'{getattr(type(error), "__module__", "Unknown")}.{getattr(type(error), "__name__", "Unknown")}'
            
            if "--development" in sys.argv:
                await ctx.send(
                    embed=embed.error_embed(f'{user} - {cog_name}.{command_name}: {error_type} => {tb} => {error}'),
                    ephemeral=True
                )
            else:
                await ctx.send(
                    embed=embed.error_embed('An error occured.'),
                    ephemeral=True
                )

            self.logger.error(f'{user} - {cog_name}.{command_name}: {error_type} => {tb} => {error}')

            self.metrics_handler.error_counter.labels(
                cog=cog_name,
                command=command_name,
                error=error_type,
            ).inc()
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

        if "--development" not in sys.argv:
            await self.pool.wait_closed()
            await self.redis.close()

        logging.shutdown()
        await super().close()


bot = Bot()

@bot.command()
@commands.is_owner()
async def cogs(ctx):
    await ctx.send(embed=discord.Embed(
        color=0,
        title='Cogs',
        description='\n'.join(fetch_cogs())
    ))

@bot.command()
@commands.is_owner()
async def load(ctx, cog):
    cog_path = f'cogs.{cog}'
    try:
        await bot.unload_extension(cog_path)
    except commands.ExtensionNotLoaded:
        pass
    
    try:
        await bot.load_extension(cog_path)
    except commands.ExtensionNotFound:
        await ctx.send(embed=embed.error_embed(f'Cog not found.'))
    except commands.NoEntryPointError:
        await ctx.send(embed=embed.error_embed(f'Cog has syntax errors.'))
    except Exception as e:
        await ctx.send(embed=embed.error_embed(f'Error: {type(e)} | {e}'))
    else:
        importlib.reload(embed)
        await ctx.send(embed=embed.success_embed(f'Loaded **{cog_path}**.'))
    
@bot.command()
@commands.is_owner()
async def unload(ctx, cog):
    cog_path = f'cogs.{cog}'
    try:
        await bot.unload_extension(cog_path)
    except commands.ExtensionNotLoaded:
        await ctx.send(embed=embed.error_embed(f'Cog is not loaded.'))
    else:
        await ctx.send(embed=embed.success_embed(f'Unloaded **{cog_path}**.'))

@bot.command()
@commands.is_owner()
async def sync(ctx):
    await ctx.send(embed=embed.success_embed(f'Attempt to sync sent.'))
    await bot.tree.sync()


bot.run(os.getenv('TEST_TOKEN') if "--development" in sys.argv else os.getenv('TOKEN'))
