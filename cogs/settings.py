import disnake
from disnake.ext import commands
from disnake.ext.commands import Param

import core.tools
from core.tools import LangTool, is_guild_owner, has_permissions
from core.database import cur, redis_client
from core.exceptions import *
from core.guild_data import GuildData, get_locale
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
            guild_locale = await get_locale(inter.guild.id)
            locale = LangTool(guild_locale)
            await inter.send(locale["exceptions.NotGuildOwner"])

    @commands.cooldown(1, 360, commands.BucketType.guild)
    @settings.sub_command(description="установить язык бота")
    async def language(self, inter: disnake.ApplicationCommandInteraction,
                       locale: str = Param(autocomplete=autocomplete_locales)):
        guild_locale = await get_locale(inter.guild.id)
        locale_ = LangTool(guild_locale)
        if locale in locales:
            await cur("query", f"UPDATE `guilds` SET `locale` = '{locale}' WHERE `guild` = {inter.guild.id}")
            await redis_client.set(inter.guild.id, locale)
            await inter.send(locale_["settings.setLocale"].format(locale))
        else:
            await inter.send(locale_["settings.invalidLocale"])

    @commands.cooldown(1, 200, commands.BucketType.guild)
    @settings.sub_command(description="включить/отключить новости бота")
    async def news(self, inter: disnake.ApplicationCommandInteraction,
                   status: str = Param(autocomplete=autocomplete_statuses),
                   channel: disnake.TextChannel = Param(default=None,
                                                        description="канал куда будут поступать новости")):
        channel_ = channel or inter.channel
        guild_locale = await get_locale(inter.guild.id)
        locale = LangTool(guild_locale)
        if status == "on":
            webhooks = await inter.guild.webhooks()
            is_created, news = core.tools.news_status(webhooks)
            if not is_created:
                source = self.client.get_channel(917015010801238037)
                news: disnake.Webhook = await source.follow(destination=channel_)
                await news.edit(name="FlooryNews")
                await inter.send(locale["settings.newsOn"])
            else:
                await inter.send(locale["settings.alreadyCreated"])

        elif status == "off":
            webhooks = await inter.guild.webhooks()
            is_created, news = core.tools.news_status(webhooks)
            if is_created:
                await news.delete()
                await inter.send(locale["settings.newsOff"])
            else:
                await inter.send(locale["settings.notCreatedYet"])
        else:
            await inter.send(locale["settings.invalidArg"])

    @commands.cooldown(1, 120, commands.BucketType.guild)
    @settings.sub_command(description="изменить канал для новостей")
    async def set_news_channel(self, inter: disnake.ApplicationCommandInteraction,
                               channel: disnake.TextChannel = Param(description="канал куда будут поступать новости")):
        guild_locale = await get_locale(inter.guild.id)
        locale = LangTool(guild_locale)
        webhooks = await inter.guild.webhooks()
        is_created, news = core.tools.news_status(webhooks)
        if not is_created:
            await inter.send(locale["settings.newsNotCreatedYet"])
        else:
            await news.edit(channel=channel)
            await inter.send(locale["settings.setNewsChannel"])

    @commands.cooldown(1, 120, commands.BucketType.guild)
    @settings.sub_command(description="включить/выключить логирование")
    async def logging(self, inter: disnake.ApplicationCommandInteraction,
                      status: str = commands.Param(autocomplete=autocomplete_statuses),
                      channel: disnake.TextChannel = commands.Param(description="канал куда будут поступать логи")):
        guild_data = GuildData(inter.guild.id)
        await guild_data.set_all()
        locale = LangTool(guild_data.locale)
        if status == 'on':
            if guild_data.logging == 'false':
                await cur("query", f"UPDATE `guilds` SET `logging` = 'true' WHERE `guild` = {inter.guild.id}")
                await cur("query",
                          f"UPDATE `guilds` SET `logs-channel` = {channel.id} WHERE `guild` = {inter.guild.id}")
                await inter.send(locale["settings.logsEnabled"])
            else:
                await inter.send(locale["settings.logsAlreadyEnabled"])
        elif status == 'off':
            if guild_data.logging == 'true':
                await cur("query", f"UPDATE `guilds` SET `logging` = 'false' WHERE `guild` = {inter.guild.id}")
                await inter.send(locale["settings.logsTurnedOff"])
            else:
                await inter.send(locale["settings.logsAlreadyOff"])
        else:
            await inter.send(locale["settings.invalidArg"])

    @commands.cooldown(1, 120, commands.BucketType.guild)
    @settings.sub_command(description="настроить канала логирования")
    async def logs_channel(self, inter: disnake.ApplicationCommandInteraction,
                           channel: disnake.TextChannel = commands.Param(
                               description="канал куда будут поступать логи")):
        guild_data = GuildData(inter.guild.id)
        await guild_data.set_all()
        locale = LangTool(guild_data.locale)
        if guild_data.logging == 'false':
            await inter.send(locale["settings.logsNotEnabledYet"])
        else:
            await cur("query", f"UPDATE `guilds` SET `logs-channel` = {channel.id} WHERE `guild` = {inter.guild.id}")
            await inter.send(locale["settings.setLogsChannel"])


def setup(client):
    client.add_cog(Settings(client))
