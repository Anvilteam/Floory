import disnake
import datetime
from disnake.ext import commands
from core.tools import is_higher, translated, COLORS
from core.cooldown import DynamicCooldown
from core.guild_data import get_locale, GuildData
from core.exceptions import *

__file__ = "cogs/moderation/locales"


@translated(__file__)
class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.dynamic_cooldown(DynamicCooldown(1, 90), commands.BucketType.member)
    @is_higher()
    @commands.slash_command()
    async def moderation(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @moderation.after_invoke
    async def mod_logs(self, inter: disnake.ApplicationCommandInteraction):
        if not inter.command_failed:
            gd = GuildData(inter.guild_id)
            await gd.set_all()
            if gd.logging == 'true' and gd.logs_channel != 'None':
                channel = inter.guild.get_channel(int(gd.logs_channel))
                embed = disnake.Embed(title=self.lang[gd.locale]["mod_logs"].format(member=inter.filled_options['member'],
                                                                                    author=inter.author),
                                      color=COLORS["default"])
                embed.add_field(self.lang[gd.locale]["command"], f"> {inter.application_command.name}")
                await channel.send(embed=embed)

    @commands.has_permissions(kick_members=True)
    @moderation.sub_command(description="выгнать участника с сервера")
    async def kick(self, inter: disnake.ApplicationCommandInteraction,
                   member: disnake.Member = commands.Param(description='пользователь'),
                   reason: str = commands.Param(default=None, description='причина')):
        locale = await get_locale(inter.guild.id)
        author = inter.author
        reason_ = reason or self.lang[locale]["reasonIsNone"]
        await inter.channel.purge(limit=1)
        await member.kick(reason=reason)
        log = self.lang[locale]["kick"].format(author=author, member=member,
                                               reason=reason_)
        await inter.send(log)

    @commands.has_permissions(ban_members=True)
    @moderation.sub_command(description="забанить участника")
    async def ban(self, inter: disnake.ApplicationCommandInteraction,
                  member: disnake.Member = commands.Param(description='пользователь'),
                  reason: str = commands.Param(default=None, description='причина')):
        locale = await get_locale(inter.guild.id)
        author = inter.author
        reason_ = reason or self.lang[locale]["reasonIsNone"]
        await member.ban(reason=reason)
        log = self.lang[locale]["ban"].format(author=author, member=member,
                                              reason=reason_)
        await inter.send(log)

    @commands.has_permissions(moderate_members=True)
    @moderation.sub_command(description="мут участника")
    async def mute(self, inter: disnake.ApplicationCommandInteraction,
                   member: disnake.Member = commands.Param(description='пользователь'),
                   seconds: float = 0,
                   minutes: float = 1,
                   hours: int = 0,
                   days: int = 0,
                   reason: str = commands.Param(default=None, description='причина')):
        locale = await get_locale(inter.guild.id)
        author = inter.author
        timeout = datetime.timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days)
        reason_ = reason or self.lang[locale]["reasonIsNone"]
        await member.timeout(duration=timeout, reason=reason_)
        log = self.lang[locale]["mute"].format(member=member, author=author, reason=reason_)
        await inter.send(log)

    @commands.has_permissions(moderate_members=True)
    @moderation.sub_command(description="размут участника")
    async def unmute(self, inter: disnake.ApplicationCommandInteraction,
                     member: disnake.Member = commands.Param(description='пользователь')):
        locale = await get_locale(inter.guild.id)
        author = inter.author
        await member.timeout(duration=0)
        log = self.lang[locale]["unmute"].format(member=member, author=author)
        await inter.send(log)

    @commands.dynamic_cooldown(DynamicCooldown(1, 90), commands.BucketType.member)
    @commands.has_permissions(manage_messages=True)
    @commands.slash_command(description="очистка чата на указанное кол-во сообщений")
    async def clear(self, inter: disnake.ApplicationCommandInteraction,
                    amount: int = commands.Param(default=1, description='кол-во сообщений (макс. 250)', lt=251),
                    member: disnake.Member = commands.Param(default=None,
                                                            description='сообщения какого пользователя надо очистить')):
        await inter.response.defer()
        await inter.delete_original_message()
        if member:
            if inter.author.top_role > member.top_role or inter.author == member:
                await inter.channel.purge(limit=amount, check=lambda m: m.author == member)
        else:
            await inter.channel.purge(limit=amount)
