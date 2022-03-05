import disnake
import datetime
from disnake.ext import commands
from core.tools import LangTool, has_permissions, color_codes
from core.exceptions import *


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 90, commands.BucketType.member)
    @commands.slash_command()
    async def moderation(self, inter):
        pass

    @has_permissions('kick_members')
    @moderation.sub_command(description="выгнать участника с сервера")
    async def kick(self, inter: disnake.ApplicationCommandInteraction,
                   member: disnake.Member = commands.Param(description='пользователь'),
                   reason: str = commands.Param(default=None, description='причина')):
        locale = LangTool(inter.guild.id)
        await locale.set()
        author = inter.author
        if reason is None:
            reason = locale["moderation.reasonIsNone"]
        await inter.channel.purge(limit=1)
        await member.kick(reason=reason)
        await inter.send(locale["moderation.kick"].format(author=author, member=member,
                                                          reason=reason))

    @has_permissions('ban_members')
    @moderation.sub_command(description="забанить участника")
    async def ban(self, inter,
                  member: disnake.Member = commands.Param(description='пользователь'),
                  reason: str = commands.Param(default=None, description='причина')):
        locale = LangTool(inter.guild.id)
        await locale.set()
        author = inter.author
        if reason is None:
            reason = locale["moderation.reasonIsNone"]
        await member.ban(reason=reason)
        await inter.send(locale["moderation.ban"].format(author=author, member=member,
                                                         reason=reason))

    @has_permissions('moderate_members')
    @moderation.sub_command(description="мут/размут участника")
    async def mute(self, inter: disnake.ApplicationCommandInteraction,
                   member: disnake.Member = commands.Param(description='пользователь'),
                   seconds: float = 0,
                   minutes: float = 1,
                   hours: int = 0,
                   days: int = 0,
                   reason: str = commands.Param(default=None, description='причина')):
        locale = LangTool(inter.guild.id)
        await locale.set()
        author = inter.author
        if member.current_timeout is None:
            timeout = datetime.timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days)
            if reason is None:
                reason = locale["moderation.reasonIsNone"]
            await member.timeout(duration=timeout, reason=reason)
            await inter.send(locale["moderation.mute"].format(member=member, author=author, reason=reason))
        else:
            await member.timeout(duration=0)
            await inter.send(locale["moderation.unmute"].format(member=member, author=author))

    @commands.cooldown(1, 90, commands.BucketType.member)
    @has_permissions('manage_messages', position_check=False)
    @commands.slash_command(description="очистка чата на указанное кол-во сообщений")
    async def clear(self, inter: disnake.ApplicationCommandInteraction,
                    amount: int = commands.Param(default=1, description='кол-во сообщений')):
        if amount < 251:
            await inter.response.defer()
            await inter.delete_original_message()
            await inter.channel.purge(limit=amount)
        else:
            locale = LangTool(inter.guild.id)
            await locale.set()
            await inter.send(locale["tmь"])


def setup(client):
    client.add_cog(Moderation(client))
