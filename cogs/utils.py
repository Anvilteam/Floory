import string
import disnake
import random
from disnake.ext import commands
from disnake.ext.commands import Param
from core.tools import LangTool, perms_to_dict, has_permissions, is_guild_owner


class Utils(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command()
    async def utils(self, inter):
        pass

    @utils.sub_command(description="получение информации о пользователе")
    async def member(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
        locale = LangTool(inter.guild.id)
        guild_owner = inter.guild.owner
        name = member.name
        created_at = member.created_at.strftime('%Y.%m.%d %H:%M:%S')
        joined_at = member.joined_at.strftime('%Y.%m.%d %H:%M:%S')
        top_role = member.top_role.mention
        if member == guild_owner:
            is_owner = locale["main.true"]
        else:
            is_owner = locale["main.false"]
        embed = disnake.Embed(title="📖 " + locale["utils.statistics"] + str(member),
                              color=0x3ef0a9)
        embed.add_field(name="✒ " + locale["utils.real_name"],
                        value=name)
        embed.add_field(name="⏳ " + locale["utils.uCreated_at"],
                        value=created_at)
        embed.add_field(name="📆 " + locale["utils.joined_at"],
                        value=joined_at, inline=False)
        embed.add_field(name="🏆 " + locale["utils.top_role"],
                        value=top_role)
        embed.add_field(name="👑 " + locale["utils.is_owner"],
                        value=is_owner, inline=False)
        await inter.send(embed=embed, delete_after=30.0)

    @utils.sub_command(description="информация о сервере")
    async def server(self, inter: disnake.ApplicationCommandInteraction):
        locale = LangTool(inter.guild.id)
        guild = inter.guild
        name = guild.name
        members = len(guild.members)
        icon = guild.icon
        owner = guild.owner

        def online(member=guild.members):
            return member.status != disnake.Status.offline and not member.bot

        members_list = list(filter(online, guild.members))
        online_list = len(members_list)

        def members(member=guild.members):
            return member and not member.bot

        users_list = list(filter(members, guild.members))
        members_count = len(users_list)
        created_at = guild.created_at.strftime('%Y.%m.%d %H:%M:%S')
        embed = disnake.Embed(title="📖 " + locale["utils.statistics"], color=0x3ef0a9)
        embed.add_field(name=locale["main.guild"], value=f"```{guild} | {guild.id}```")
        embed.add_field(name="👑 " + locale["utils.is_owner"][:-1],
                        value=f"```{owner}```", inline=False)
        embed.add_field(name="👥 " + locale["utils.members_amount"],
                        value=f"``` {locale['utils.total']} {members_count} | {locale['utils.online']} {online_list}```",
                        inline=True)
        embed.add_field(name="⏳ " + locale["utils.sCreated_at"],
                        value=f"```{created_at}```", inline=False)
        if icon is None:
            embed.set_thumbnail(file=disnake.File("logo.png"))
        else:
            embed.set_thumbnail(url=str(icon))
        await inter.send(embed=embed, delete_after=30.0)

    @has_permissions("manage_roles", position_check=False)
    @utils.sub_command(description="получение прав конкретного пользователя")
    async def permissions(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
        emojies = {0: '❌', 1: '✅'}
        lang = LangTool(inter.guild.id)
        member_perms = perms_to_dict(member.guild_permissions)
        # '❌|✅', 'permission translate', 'new line'
        embed_value = "".join(
            [f"{emojies[member_perms[perm]]} {lang[f'permissions.{perm}']}\n" for perm in member_perms])
        embed = disnake.Embed(title=lang["utils.members_permissions"].format(member=member),
                              color=0x3ef0a9)
        embed.add_field(name=lang["utils.perms_list"], value=embed_value)
        await inter.send(embed=embed, delete_after=30.0)

    @utils.sub_command(description="получение аватара пользователя")
    async def avatar(self, inter: disnake.ApplicationCommandInteraction,
                     member: disnake.Member):
        embed = disnake.Embed(title=member, color=0x3ef0a9)
        embed.set_image(url=member.display_avatar.url)
        await inter.response.send_message(embed=embed)

    @has_permissions("administrator", position_check=False)
    @utils.sub_command(description="сделать голосование")
    async def voting(self, inter: disnake.ApplicationCommandInteraction,
                     title: str = Param(description="название голосования"),
                     description: str = Param(description="описание голосования"),
                     image: disnake.Attachment = Param(default=None, description="картинка (по желанию)"),
                     variants: str = Param(default="варианты для голосование (через '|')")):
        locale = LangTool(inter.guild.id)
        view = disnake.ui.View()
        embed = disnake.Embed(title=title, description=description)
        vars = variants.split('|')
        if len(vars) < 5:
            for var in vars:
                embed.add_field(name=var, value='-----')
                custom_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(int(4)))
                btn = disnake.ui.Button(label=var + '|0', custom_id=f'voting-{custom_id}-{inter.id}')
                view.add_item(btn)
            view.add_item(disnake.ui.Button(label=locale["utils.closeVoting"], style=disnake.ButtonStyle.red,
                                            custom_id='close_vote', emoji='❌'))
            if image is not None and image.content_type == 'image/png':
                embed.set_image(image.url)
            embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
            await inter.send(embed=embed, view=view)
        else:
            await inter.send(locale['utils.tmButtons'])


def setup(client):
    client.add_cog(Utils(client))
