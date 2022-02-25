import disnake
import logging
import os
from disnake.ext import commands
from core.tools import is_bot_developer
from core.database import cur
from core.exceptions import *

logger = logging.getLogger(__name__)


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

    @dev.sub_command()
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
            except commands.ExtensionNotFound:
                await inter.send(f"Ког {cog} не найден")

    @dev.sub_command()
    async def make_news(self, inter, title, descr, field_title=None, field_value=None, footer=None, image=None):
        embed = disnake.Embed(title=title, description=descr)
        if field_title is not None and field_value is not None:
            embed.add_field(field_title, field_value)
        if image is not None:
            embed.set_image(image)
        if footer is not None:
            embed.set_footer(text=footer)
        for guild in self.client.guilds:
            news_channel = await cur("fetch", f"SELECT `news-channel` FROM `guilds` WHERE guild = {guild.id}")[0]
            if news_channel is not None:
                print(news_channel)
                channel = disnake.utils.get(guild.text_channels, id=news_channel)
                await channel.send(embed=embed)
        await inter.send("успешно")


def setup(client):
    client.add_cog(Dev(client))
