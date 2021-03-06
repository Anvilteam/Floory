import disnake
import logging
import os
from disnake.ext import commands
from core.tools import is_bot_developer, COLORS
from core.database import cur, redis_client
from core.exceptions import *
from loguru import logger


class Dev(commands.Cog):
    def __init__(self, client):
        self.client = client

    @is_bot_developer()
    @commands.slash_command()
    async def dev(self, inter):
        pass

    @dev.error
    async def dev_error(self, inter, error):
        if isinstance(error, NotDeveloper):
            await inter.send("You are not bot developer")

    @dev.sub_command(description="получить кэш гильдии")
    async def get_cache(self, inter: disnake.ApplicationCommandInteraction):
        cache = (await redis_client.lrange(inter.guild.id, 0, 2))[::-1]
        await inter.send(' '.join(cache))

"""    @dev.sub_command(description="перезагрузить один или все коги")
    async def reload_cog(self, inter: disnake.ApplicationCommandInteraction,
                         cog: str = commands.Param(default=None, description="Ког для перезагрузки, если не указан то "
                                                                             "перезагружаются все")):
        if cog is None:
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py') and filename != 'dev.py':
                    self.client.reload_extension(f'cogs.{filename[:-3]}')
                    logger.info(f"Ког {filename} перезагружен")
            await inter.send(f"Коги успешно перезагружены")
        else:
            try:
                self.client.reload_extension(f'cogs.{cog}')
                await inter.send(f"Ког {cog} успешно перезагружен")
                logger.info(f"Ког {cog} успешно перезагружен")
            except commands.ExtensionNotFound:
                await inter.send(f"Ког {cog} не найден")"""

