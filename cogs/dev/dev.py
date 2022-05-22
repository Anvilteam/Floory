import disnake
import logging
import os
from disnake.ext import commands
from core.checks import is_bot_developer
from core.guild_data import GuildData
from core.exceptions import *
from loguru import logger


class Dev(commands.Cog):
    def __init__(self, client):
        self.client = client

    @is_bot_developer()
    @commands.slash_command()
    async def dev(self, inter):
        pass

    @dev.sub_command(description="получить кэш гильдии")
    async def get_cache(self, inter: disnake.ApplicationCommandInteraction):
        cache = await GuildData.from_cache(inter.guild_id)
        await inter.send(f"{cache.logging}, {cache.logs_channel}")