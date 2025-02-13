import discord


def default_embed(message):
    return discord.Embed(
        colour=0,
        description=message
    )

def error_embed(message):
    return discord.Embed(
        colour=discord.Color.red(),
        description=message
    )

def success_embed(message):
    return discord.Embed(
        colour=discord.Color.green(),
        description=message
    )
