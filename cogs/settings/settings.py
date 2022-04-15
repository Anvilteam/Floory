import disnake
from disnake.ext import commands
from disnake.ext.commands import Param

import core.tools
from core.tools import LangTool, is_guild_owner, translated
from core.database import cur, redis_client
from core.exceptions import *
from core.guild_data import get_locale, refresh
from typing import List

__file__ = "cogs/settings/locales"

modules_status = ["on", "off"]
locales = ["ru_RU", "en_US"]


async def autocomplete_statuses(inter, string: str) -> List[str]:
    return [status for status in modules_status if string.lower() in status.lower()]


async def autocomplete_locales(inter, string: str) -> List[str]:
    return [locale for locale in locales if string.lower() in locale.lower()]


@translated(__file__)
class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.has_permissions(administrator=True)
    @commands.slash_command()
    async def settings(self, inter):
        pass

    @settings.error
    async def settings_errors(self, inter, error):
        if isinstance(error, NotGuildOwner):
            locale = await get_locale(inter.guild.id)
            await inter.send(self.lang[locale]["NotGuildOwner"])

    @commands.cooldown(1, 360, commands.BucketType.guild)
    @settings.sub_command(description="установить язык бота")
    async def language(self, inter: disnake.ApplicationCommandInteraction,
                       locale: str = Param(autocomplete=autocomplete_locales)):
        locale_ = await get_locale(inter.guild.id)
        if locale in locales:
            await cur("query", f"UPDATE `guilds` SET `locale` = '{locale}' WHERE `guild` = {inter.guild.id}")
            await refresh(inter.guild.id, locale=locale)
            await inter.send(self.lang[locale_]["setLocale"].format(locale))
        else:
            await inter.send(self.lang[locale_]["invalidLocale"])

    @commands.cooldown(1, 200, commands.BucketType.guild)
    @settings.sub_command(description="включить/отключить новости бота")
    async def news(self, inter: disnake.ApplicationCommandInteraction,
                   status: str = Param(autocomplete=autocomplete_statuses),
                   channel: disnake.TextChannel = Param(default=None,
                                                        description="канал куда будут поступать новости")):
        channel_ = channel or inter.channel
        locale = await get_locale(inter.guild.id)
        if status == "on":
            webhooks = await inter.guild.webhooks()
            is_created, news = core.tools.news_status(webhooks)
            if not is_created:
                source = self.client.get_channel(917015010801238037)
                news: disnake.Webhook = await source.follow(destination=channel_)
                await news.edit(name="FlooryNews")
                await inter.send(self.lang[locale]["newsOn"])
            else:
                await inter.send(self.lang[locale]["alreadyCreated"])

        elif status == "off":
            webhooks = await inter.guild.webhooks()
            is_created, news = core.tools.news_status(webhooks)
            if is_created:
                await news.delete()
                await inter.send(self.lang[locale]["newsOff"])
            else:
                await inter.send(self.lang[locale]["notCreatedYet"])
        else:
            await inter.send(self.lang[locale]["invalidArg"])

    @commands.cooldown(1, 120, commands.BucketType.guild)
    @settings.sub_command(description="изменить канал для новостей")
    async def set_news_channel(self, inter: disnake.ApplicationCommandInteraction,
                               channel: disnake.TextChannel = Param(description="канал куда будут поступать новости")):
        locale = await get_locale(inter.guild.id)
        webhooks = await inter.guild.webhooks()
        is_created, news = core.tools.news_status(webhooks)
        if not is_created:
            await inter.send(self.lang[locale]["newsNotCreatedYet"])
        else:
            await news.edit(channel=channel)
            await inter.send(self.lang[locale]["setNewsChannel"])

