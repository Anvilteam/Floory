import disnake
from disnake.ext import commands
from disnake.ext.commands import Param
import core.tools
from core.tools import translated
from core.cooldown import DynamicCooldown
from core.database import cur, redis_client
from core.exceptions import *
from core.guild_data import get_locale, refresh, GuildData

__file__ = "cogs/settings/locales"

locales = ["ru_RU", "en_US"]


@translated(__file__)
class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.has_permissions(administrator=True)
    @commands.slash_command()
    async def settings(self, inter):
        pass

    @settings.after_invoke
    async def settings_logs(self, inter: disnake.ApplicationCommandInteraction):
        if not inter.command_failed:
            gd = GuildData(inter.guild_id)
            await gd.set_all()
            if gd.logging == 'true' and gd.logs_channel != 'None':
                channel = inter.guild.get_channel(int(gd.logs_channel))
                if channel is not None:
                    check = False
                    match channel.overwrites_for(inter.guild.me.top_role).send_messages:
                        case True:
                            check = True
                        case None:
                            check = True if inter.guild.me.guild_permissions.send_messages else False
                    if check:
                        embed = disnake.Embed(title=self.lang[gd.locale]["settings_logs"].format(author=inter.author))
                        options = map(lambda k: f"{k}:{inter.filled_options[k]}", inter.filled_options.keys())
                        embed.description = f"`/{inter.application_command.qualified_name} " + " ".join(options) + '`'
                        await channel.send(embed=embed)

    @settings.error
    async def settings_errors(self, inter, error):
        if isinstance(error, NotGuildOwner):
            locale = await get_locale(inter.guild.id)
            await inter.send(self.lang[locale]["NotGuildOwner"])

    @commands.dynamic_cooldown(DynamicCooldown(1, 150), commands.BucketType.member)
    @settings.sub_command(description="установить язык бота")
    async def language(self, inter: disnake.ApplicationCommandInteraction,
                       locale: str = Param(choices=locales)):
        locale_ = await get_locale(inter.guild.id)
        if locale in locales:
            await cur("query", f"UPDATE `guilds` SET `locale` = '{locale}' WHERE `guild` = {inter.guild.id}")
            await refresh(inter.guild.id, locale=locale)
            await inter.send(self.lang[locale_]["setLocale"].format(locale))

    @commands.dynamic_cooldown(DynamicCooldown(1, 60), commands.BucketType.member)
    @settings.sub_command_group(description="включить/отключить новости бота")
    async def news(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @news.sub_command(description="включить новости")
    async def news_on(self, inter: disnake.ApplicationCommandInteraction,
                      channel: disnake.TextChannel = commands.Param(description="канал куда будут поступать новости")):
        locale = await get_locale(inter.guild_id)
        webhooks = await inter.guild.webhooks()
        is_created, news = core.tools.news_status(webhooks)
        if not is_created:
            source = self.client.get_channel(917015010801238037)
            news: disnake.Webhook = await source.follow(destination=channel)
            await news.edit(name="FlooryNews")
            await inter.send(self.lang[locale]["newsOn"])
            return
        await inter.send(self.lang[locale]["alreadyCreated"])

    @news.sub_command(description="выключить новости")
    async def news_off(self, inter: disnake.ApplicationCommandInteraction):
        locale = await get_locale(inter.guild_id)
        webhooks = await inter.guild.webhooks()
        is_created, news = core.tools.news_status(webhooks)
        if is_created:
            await news.delete()
            await inter.send(self.lang[locale]["newsOff"])
            return
        await inter.send(self.lang[locale]["notCreatedYet"])

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

    @commands.dynamic_cooldown(DynamicCooldown(1, 60), commands.BucketType.member)
    @settings.sub_command_group()
    async def logging(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @logging.sub_command(description="включить логирование")
    async def logs_on(self, inter: disnake.ApplicationCommandInteraction):
        guild_data = GuildData(inter.guild_id)
        await guild_data.set_all()
        if guild_data.logging == 'false':
            await cur("query", f"UPDATE `guilds` SET `logging` = 'true' WHERE `guild` = {inter.guild.id}")
            await refresh(inter.guild_id, logging='true')
            await inter.send(self.lang[guild_data.locale]["logsEnabled"])
            return
        await inter.send(self.lang[guild_data.locale]["logsAlreadyEnabled"])

    @logging.sub_command(description="выключить логирование")
    async def logs_off(self, inter: disnake.ApplicationCommandInteraction):
        guild_data = GuildData(inter.guild_id)
        await guild_data.set_all()
        if guild_data.logging == 'true':
            await cur("query", f"UPDATE `guilds` SET `logging` = 'false' WHERE `guild` = {inter.guild.id}")
            await refresh(inter.guild_id, logging='false')
            await inter.send(self.lang[guild_data.locale]["logsTurnedOff"])
            return
        await inter.send(self.lang[guild_data.locale]["logsAlreadyOff"])

    @logging.sub_command(description="изменить канал для логов")
    async def set_channel(self, inter: disnake.ApplicationCommandInteraction,
                          channel: disnake.TextChannel = commands.Param(description="канал куда будут поступать логи")):
        locale = await get_locale(inter.guild_id)
        await cur("query", f"UPDATE `guilds` SET `logs-channel` = {channel.id} WHERE `guild` = {inter.guild.id}")
        await refresh(inter.guild_id, logs_channel=channel.id)
        await inter.send(self.lang[locale]["setLogsChannel"])
