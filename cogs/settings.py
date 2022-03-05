import disnake
from disnake.ext import commands
from disnake.ext.commands import Param

import core.tools
from core.tools import LangTool, is_guild_owner, has_permissions
from core.database import cur
from core.exceptions import *
from typing import List

modules_status = ["on", "off"]
locales = ["ru_RU", "en_US"]


async def autocomplete_statuses(inter, string: str) -> List[str]:
    return [status for status in modules_status if string.lower() in status.lower()]


async def autocomplete_locales(inter, string: str) -> List[str]:
    return [locale for locale in locales if string.lower() in locale.lower()]


class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client

    @has_permissions('administrator', position_check=False)
    @commands.slash_command()
    async def settings(self, inter):
        pass

    @settings.error
    async def config_errors(self, inter, error):
        if isinstance(error, NotGuildOwner):
            locale = LangTool(inter.guild.id)
            await inter.send(locale["exceptions.NotGuildOwner"])

    @commands.cooldown(1, 360, commands.BucketType.guild)
    @settings.sub_command(description="установить язык бота")
    async def language(self, inter: disnake.ApplicationCommandInteraction,
                       locale: str = Param(autocomplete=autocomplete_locales)):
        locale_ = LangTool(inter.guild.id)
        await locale_.set()
        if locale in locales:
            await cur("query", f"UPDATE `guilds` SET `locale` = '{locale}' WHERE `guild` = {inter.guild.id}")
            await inter.send(locale_["settings.set_locale"].format(locale))
        else:
            await inter.send(locale_["settings.invalid_locale"])

    @commands.cooldown(1, 200, commands.BucketType.guild)
    @settings.sub_command(description="включить/отключить новости бота")
    async def news(self, inter: disnake.ApplicationCommandInteraction,
                   status: str = Param(autocomplete=autocomplete_statuses),
                   channel: disnake.TextChannel = Param(default=None,
                                                        description="канал куда будут поступать новости")):
        if channel is None:
            channel = inter.channel
        locale = LangTool(inter.guild.id)
        await locale.set()
        if status == "on":
            webhooks = await inter.guild.webhooks()
            is_created, news = core.tools.news_status(webhooks)
            if not is_created:
                source = self.client.get_channel(917015010801238037)
                news: disnake.Webhook = await source.follow(destination=channel)
                await news.edit(name="FlooryNews")
                await inter.send(locale["news_on"])
            else:
                await inter.send(locale["settings.alreadyCreated"])

        elif status == "off":
            webhooks = await inter.guild.webhooks()
            is_created, news = core.tools.news_status(webhooks)
            if is_created:
                await news.delete()
                await inter.send(locale["news_off"])
            else:
                await inter.send(locale["settings.notCreatedYet"])
        else:
            await inter.send(locale["settings.invalid_arg"])

    @commands.cooldown(1, 120, commands.BucketType.guild)
    @settings.sub_command(description="изменить канал для новостей")
    async def set_news_channel(self, inter: disnake.ApplicationCommandInteraction,
                               channel: disnake.TextChannel = Param(description="канал куда будут поступать новости")):
        locale = LangTool(inter.guild.id)
        await locale.set()
        webhooks = await inter.guild.webhooks()
        is_created, news = core.tools.news_status(webhooks)
        if not is_created:
            await inter.send(locale["notCreatedYet"])
        else:
            await news.edit(channel=channel)
            await inter.send(locale["settings.set_news_channel"])


def setup(client):
    client.add_cog(Settings(client))
