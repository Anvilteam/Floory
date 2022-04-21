import string
import disnake
import random
from disnake.ext import commands
from disnake.ext.commands import Param

import core.views
from core.tools import perms_to_dict, translated, dev_cooldown, tes_col
from core.guild_data import get_locale
from core.cooldown import DynamicCooldown

__file__ = "cogs/utils/locales"
cooldown = DynamicCooldown(1, 45)


@translated(__file__, "locales/permissions", "locales/main")
class Utils(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command()
    async def utils(self, inter):
        pass

    @utils.sub_command(description="получение информации о пользователе")
    async def member(self, inter: disnake.ApplicationCommandInteraction,
                     member: disnake.Member = commands.Param(description='пользователь')):
        locale = await get_locale(inter.guild.id)
        guild_owner = inter.guild.owner
        name = member.name
        created_at = member.created_at.strftime('%Y.%m.%d %H:%M:%S')
        joined_at = member.joined_at.strftime('%Y.%m.%d %H:%M:%S')
        top_role = member.top_role.mention
        if member == guild_owner:
            is_owner = self.lang[locale]["true"]
        else:
            is_owner = self.lang[locale]["false"]
        embed = disnake.Embed(title="📖 " + self.lang[locale]["statistics"] + str(member),
                              color=0x3ef0a9)
        embed.add_field(name="✒ " + self.lang[locale]["real_name"],
                        value=name)
        embed.add_field(name="⏳ " + self.lang[locale]["uCreated_at"],
                        value=created_at)
        embed.add_field(name="📆 " + self.lang[locale]["joined_at"],
                        value=joined_at, inline=False)
        embed.add_field(name="🏆 " + self.lang[locale]["top_role"],
                        value=top_role)
        embed.add_field(name="👑 " + self.lang[locale]["is_owner"],
                        value=is_owner, inline=False)
        await inter.send(embed=embed, delete_after=30.0)

    @utils.sub_command(name="server", description="информация о сервере")
    async def server(self, inter: disnake.ApplicationCommandInteraction):
        locale = await get_locale(inter.guild.id)
        guild = inter.guild
        icon = guild.icon
        owner = guild.owner

        def online(member):
            return member.status != disnake.Status.offline and not member.bot

        members_list = list(filter(online, guild.members))
        online_list = len(members_list)

        def members(member):
            return member and not member.bot

        users_list = list(filter(members, guild.members))
        members_count = len(users_list)
        created_at = guild.created_at.strftime('%Y.%m.%d %H:%M:%S')
        embed = disnake.Embed(title="📖 " + self.lang[locale]["statistics"], color=0x3ef0a9)
        embed.add_field(name=self.lang[locale]["guild"], value=f"```{guild} | {guild.id}```")
        embed.add_field(name="👑 " + self.lang[locale]["is_owner"][:-1],
                        value=f"```{owner}```", inline=False)
        embed.add_field(name="👥 " + self.lang[locale]["members_amount"],
                        value=f"``` {self.lang[locale]['total']} {members_count} | {self.lang[locale]['online']} {online_list}```",
                        inline=True)
        embed.add_field(name="⏳ " + self.lang[locale]["sCreated_at"],
                        value=f"```{created_at}```", inline=False)
        if icon is None:
            embed.set_thumbnail(file=disnake.File("logo.png"))
        else:
            embed.set_thumbnail(url=icon.url)
        await inter.send(embed=embed, delete_after=30.0)

    @commands.has_permissions(manage_roles=True)
    @utils.sub_command(description="получение прав конкретного пользователя")
    async def permissions(self, inter: disnake.ApplicationCommandInteraction,
                          member: disnake.Member = commands.Param(description='пользователь')):
        emojies = {0: '❌', 1: '✅'}
        locale = await get_locale(inter.guild.id)
        member_perms = perms_to_dict(member.guild_permissions)
        # '❌|✅', 'permission translate', 'new line'
        embed_value = "".join(
            [f"{emojies[member_perms[perm]]} {self.lang[locale][perm]}\n" for perm in member_perms])
        embed = disnake.Embed(title=self.lang[locale]["members_permissions"].format(member=member),
                              color=0x3ef0a9)
        embed.add_field(name=self.lang[locale]["perms_list"], value=embed_value)
        await inter.send(embed=embed, delete_after=30.0)

    @utils.sub_command(description="получение аватара пользователя")
    async def avatar(self, inter: disnake.ApplicationCommandInteraction,
                     member: disnake.Member = commands.Param(description='пользователь')):
        embed = disnake.Embed(title=member, color=0x3ef0a9)
        embed.set_image(url=member.display_avatar.url)
        await inter.response.send_message(embed=embed)

    @utils.sub_command(description="получить id всех эмодзи данного сервера")
    async def get_emojis(self, inter: disnake.ApplicationCommandInteraction):
        emojis = inter.guild.emojis
        formatted = ''
        for e in emojis:
            if e.animated:
                formatted += f"<a:{e.name}:{e.id}> `{e.id}`\n"
            else:
                formatted += f"<:{e.name}:{e.id}> `{e.id}`\n"
        await inter.send(formatted)
