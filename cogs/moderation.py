import disnake
import datetime
from disnake.ext import commands
from disnake.ext.commands import Param
from core.tools import LangTool, has_permissions, color_codes
from core.exceptions import *


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 600)
    @commands.slash_command()
    async def moderation(self, inter):
        pass

    @moderation.error
    async def mods_errors(self, inter, error):
        if isinstance(error, NotEnoughPerms):
            lang = LangTool(inter.guild.id)
            permissions = error.permissions
            embed_value = ''
            for perm in permissions:
                string = f"❌ {lang[f'permissions.{perm}']}\n"
                embed_value += string

            embed = disnake.Embed(title=lang["main.error"],
                                  description=lang["exceptions.NotEnoughPerms"],
                                  color=color_codes["error"])
            embed.add_field(name="Права", value=embed_value)
            await inter.send(embed=embed)
        elif isinstance(error, MemberHigherPermissions):
            lang = LangTool(inter.guild.id)
            embed = disnake.Embed(title=lang["main.error"],
                                  description=lang["exceptions.MemberHigherPermissions"],
                                  color=color_codes["error"])
            await inter.send(embed=embed)

    @has_permissions("kick_members")
    @moderation.sub_command(description="выгнать участника с сервера")
    async def kick(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member,
                   reason: str = None):
        lang = LangTool(inter.guild.id)
        author = inter.author
        if reason is None:
            reason = lang["moderation.reasonIsNone"]
        await inter.channel.purge(limit=1)
        await member.kick(reason=reason)
        await inter.send(lang["moderation.kick"].format(author=author, member=member,
                                                        reason=reason))

    @has_permissions("ban_members")
    @moderation.sub_command(description="забанить участника")
    async def ban(self, inter, member: disnake.Member, *, reason=None):
        lang = LangTool(inter.guild.id)
        author = inter.author
        if reason is None:
            reason = lang["moderation.reasonIsNone"]
        await member.ban(reason=reason)
        await inter.send(lang["moderation.ban"].format(author=author, member=member,
                                                       reason=reason))

    @has_permissions("moderate_members")
    @moderation.sub_command(description="мут/размут участника")
    async def mute(self, inter: disnake.ApplicationCommandInteraction,
                   member: disnake.Member = Param(description='пользователь'),
                   seconds: float = 0,
                   minutes: float = 1,
                   hours: int = 0,
                   days: int = 0,
                   reason=None):
        locale = LangTool(inter.guild.id)
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

    @has_permissions("manage_messages", position_check=False)
    @commands.slash_command(description="очистка чата на указанное кол-во сообщений")
    async def clear(self, inter: disnake.ApplicationCommandInteraction, amount: int = 1):
        await inter.response.defer()
        await inter.delete_original_message()
        await inter.channel.purge(limit=amount)


def setup(client):
    client.add_cog(Moderation(client))
