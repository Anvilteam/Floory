import disnake
import core.tools
from disnake.ext import commands
from disnake.ext.commands import Param
from core.tools import LangTool
from core.database import cur
from core.exceptions import *
from typing import List

modules_status = ["on", "off"]
locales = ["ru_RU"]


async def autocomplete_statuses(inter, string: str) -> List[str]:
    return [status for status in modules_status if string.lower() in status.lower()]


async def autocomplete_locales(inter, string: str) -> List[str]:
    return [locale for locale in locales if string.lower() in locale.lower()]


class GuildConfig(commands.Cog):
    def __init__(self, client):
        self.client = client

    @core.tools.is_guild_owner()
    @commands.slash_command()
    async def config(self, inter):
        pass

    @config.error
    async def config_errors(self, inter, error):
        if isinstance(error, NotGuildOwner):
            locale = LangTool(inter.guild.id)
            await inter.send(locale["exceptions.NotGuildOwner"])

    @commands.cooldown(1, 360)
    @config.sub_command()
    async def language(self, inter: disnake.ApplicationCommandInteraction,
                       locale: str = Param(autocomplete=autocomplete_locales)):
        lang = LangTool(inter.guild.id)
        if locale in locales:
            cur("query", f"UPDATE `guilds` SET `locale` = '{locale}' WHERE `guild` = {inter.guild.id}")
            await inter.send(lang["guild_config.set_locale"].format(locale))
        else:
            await inter.send(lang["guild_config.invalid_locale"])

    @commands.cooldown(1, 200)
    @config.sub_command()
    async def news(self, inter: disnake.ApplicationCommandInteraction,
                   status: str = Param(autocomplete=autocomplete_statuses)):
        lang = LangTool(inter.guild.id)
        match status:
            case "on":
                news_channel = cur("fetch", f"SELECT `news-channel` FROM `guilds` WHERE `guild` = {inter.guild.id}")[0]
                print(type(news_channel))
                if news_channel is not None:
                    cur("query", f"UPDATE `guilds` SET `news` = 'true' WHERE `guild` = {inter.guild.id}")
                    await inter.send(lang["guild_config.news_on"])
                else:
                    await inter.send(lang["guild_config.news_channel_req"])
            case "off":
                cur("query", f"UPDATE `guilds` SET `news` = 'false' WHERE `guild` = {inter.guild.id}")
                await inter.send(lang["guild_config.news_off"])
            case _:
                await inter.send(lang["guild_config.invalid_arg"])

    @commands.cooldown(1, 360)
    @config.sub_command()
    async def set_news_channel(self, inter: disnake.ApplicationCommandInteraction):
        lang = LangTool(inter.guild.id)
        cur("query", f"UPDATE `guilds` SET `news-channel` = {inter.channel.id} WHERE `guild` = {inter.guild.id}")
        await inter.send(lang["guild_config.set_news_channel"])


def setup(client):
    client.add_cog(GuildConfig(client))
