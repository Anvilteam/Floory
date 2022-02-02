import disnake
import datetime
from disnake.ext import commands
from disnake.ext.commands import Param
from core.tools import LangTool, has_permissions, color_codes
from core.exceptions import *


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command()
    async def moderation(self, inter):
        pass

    @moderation.error
    async def mods_errors(self, inter, error):
        if isinstance(error, NotEnoughPerms):
            lang = LangTool(inter.guild.id)
            permissions = error.permissions
            embed_value = "".join([f"❌ {lang.get_frase(f'permissions.{perm}')}\n" for perm in permissions])
            embed = disnake.Embed(title=lang.get_frase("exceptions.error"),
                                  description=lang.get_frase("exceptions.NotEnoughPerms"),
                                  color=color_codes["error"])
            embed.add_field(name="Права", value=embed_value)
            await inter.send(embed=embed)
        elif isinstance(error, MemberHigherPermissions):
            lang = LangTool(inter.guild.id)
            embed = disnake.Embed(title=lang.get_frase("exceptions.error"),
                                  description=lang.get_frase("exceptions.MemberHigherPermissions"),
                                  color=color_codes["error"])
            await inter.send(embed=embed)

    @has_permissions(["ban_members", "manage_channels"])
    @moderation.sub_command()
    async def kick(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member,
                   reason: str = None):
        lang = LangTool(inter.guild.id)
        author = inter.author
        if reason is None:
            reason = lang.get_frase("moderation.reasonIsNone")
        await inter.channel.purge(limit=1)
        await member.kick(reason=reason)
        await inter.send(lang.get_frase("moderation.kick").format(author=author, member=member,
                                                                  reason=reason))

    @has_permissions(["ban_members"])
    @moderation.sub_command()
    async def ban(self, inter, member: disnake.Member, *, reason=None):
        lang = LangTool(inter.guild.id)
        author = inter.author
        if reason is None:
            reason = lang.get_frase("moderation.reasonIsNone")
        await member.ban(reason=reason)
        await inter.send(lang.get_frase("moderation.ban").format(author=author, member=member,
                                                                 reason=reason))

    @moderation.sub_command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member, *, reason='Причина не указана'):
        author = ctx.message.author
        await ctx.channel.purge(limit=1)
        await ctx.member.unban(reason=reason)
        await ctx.send(f"Пользователь был разбанен {author} по причине {reason}")

    @has_permissions(["moderate_members"])
    @moderation.sub_command()
    async def mute(self, inter: disnake.ApplicationCommandInteraction,
                   member: disnake.Member = Param(description='пользователь'),
                   seconds: float = 0,
                   minutes: float = 1,
                   hours: int = 0,
                   days: int = 0,
                   reason=None):
        lang = LangTool(inter.guild.id)
        author = inter.author
        if member.current_timeout is None:
            timeout = datetime.timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days)
            if reason is None:
                reason = lang.get_frase("moderation.reasonIsNone")
            await member.timeout(duration=timeout, reason=reason)
            await inter.send(lang.get_frase("moderation.mute"))
        else:
            await member.timeout(duration=0)
            await inter.send(lang.get_frase("moderation.unmute"))

    @has_permissions(["manage_messages"])
    @commands.slash_command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, inter: disnake.ApplicationCommandInteraction, amount=1):
        await inter.delete_original_message()
        await inter.channel.purge(limit=amount)


def setup(client):
    client.add_cog(Moderation(client))
