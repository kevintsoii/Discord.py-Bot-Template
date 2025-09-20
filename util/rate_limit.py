import time
import functools
from typing import Optional, List, Union
from discord.ext import commands


class RateLimitExceeded(commands.CommandError):
    def __init__(self, retry_after: float):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Try again in {retry_after:.1f} seconds.")


def rate_limit(
    rate: int,
    per: int,
    *,
    user: bool = True,
    command: bool = True,
    guild: bool = False
):
    """
    Rate limiting decorator for Discord.py bot commands using token bucket strategy.
    
    Uses Redis hash to store bucket state (tokens and last refill time). Tokens are consumed
    on each request and refilled over time, allowing burst traffic up to bucket capacity.
    
    Args:
        rate (int): Maximum number of calls
        per (int): Time window (seconds)
        user (bool): Include user ID in rate limit key
        command (bool): Include command name in rate limit key
        guild (bool): Include guild ID in rate limit key
    
    Throws:
        RateLimitExceeded: If the rate limit is exceeded
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            print(ctx.bot.redis)
            if not hasattr(ctx.bot, 'redis') or ctx.bot.redis is None:
                return await func(self, ctx, *args, **kwargs)
            
            # Build rate limit key based on optional user/command/guild IDs
            key_parts = []
            
            if user and ctx.author:
                key_parts.append(f"u-{ctx.author.id}")
            
            if command and ctx.command:
                key_parts.append(f"c-{ctx.command.qualified_name}")
            
            if guild and ctx.guild:
                key_parts.append(f"g-{ctx.guild.id}")
            
            rate_limit_key = f"rate_limit:{':'.join(key_parts)}"
            
            current_time = time.time()
            refill_rate = rate / per
            
            # Atomic pipeline
            pipe = ctx.bot.redis.pipeline()
            pipe.hgetall(rate_limit_key)
            results = await pipe.execute()
            bucket_data = results[0]
            
            if bucket_data:
                tokens = float(bucket_data.get('tokens', rate))
                last_refill = float(bucket_data.get('last_refill', current_time))
                
                time_elapsed = current_time - last_refill
                tokens_to_add = time_elapsed * refill_rate
                tokens = min(rate, tokens + tokens_to_add)
            else:
                tokens = rate
                last_refill = current_time
            
            if tokens < 1:
                tokens_needed = 1 - tokens
                retry_after = tokens_needed / refill_rate
                raise RateLimitExceeded(retry_after)
            
            tokens -= 1
            
            pipe = ctx.bot.redis.pipeline()
            pipe.hset(rate_limit_key, mapping={
                'tokens': str(tokens),
                'last_refill': str(current_time)
            })
            pipe.expire(rate_limit_key, per * 2)
            await pipe.execute()
            
            return await func(self, ctx, *args, **kwargs)
        
        return wrapper
    return decorator



