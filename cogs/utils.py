import disnake
from disnake.ext import commands
from disnake.ext.commands import Param
from core.config import cCodes, EMOJI_ASSOCIATION
from core.tools import LangTool, permsToDict, perms_check


class Utils(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(description="get user info")
    async def member(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
        lang = LangTool(inter.guild.id)
        guild_owner = inter.guild.owner
        name = member.name
        created_at = member.created_at.strftime('%Y.%m.%d %H:%M:%S')
        joined_at = member.joined_at.strftime('%Y.%m.%d %H:%M:%S')
        top_role = member.top_role.mention
        if member == guild_owner:
            is_owner = lang.get_frase("main.true")
        else:
            is_owner = lang.get_frase("main.false")
        embed = disnake.Embed(title="📖 " + lang.get_frase("utils.uStatistics").format(member=member),
                              color=0x3ef0a9)
        embed.add_field(name="✒ " + lang.get_frase("utils.real_name"),
                        value=name)
        embed.add_field(name="⏳ " + lang.get_frase("utils.uCreated_at"),
                        value=created_at)
        embed.add_field(name="📆 " + lang.get_frase("utils.joined_at"),
                        value=joined_at, inline=False)
        embed.add_field(name="🏆 " + lang.get_frase("utils.top_role"),
                        value=top_role)
        embed.add_field(name="👑 " + lang.get_frase("utils.is_owner"),
                        value=is_owner, inline=False)
        await inter.response.send_message(embed=embed)

    @commands.slash_command(description="get server info")
    async def server(self, inter: disnake.ApplicationCommandInteraction):
        lang = LangTool(inter.guild.id)
        guild = inter.guild
        name = guild.name
        members = len(guild.members)
        channels = len(guild.channels)
        categories = len(guild.categories)
        icon = guild.icon
        owner = guild.owner
        created_at = guild.created_at.strftime('%Y.%m.%d %H:%M:%S')
        embed = disnake.Embed(title="📖 " + lang.get_frase("utils.sStatistics").format(guild=name), color=0x3ef0a9)
        embed.add_field(name="👥 " + lang.get_frase("utils.members_amount"),
                        value=members)
        embed.add_field(name="⚙ " + lang.get_frase("utils.chanCateg_amount"),
                        value=f'{channels}/{categories}')
        embed.add_field(name="⏳ " + lang.get_frase("utils.sCreated_at"),
                        value=created_at, inline=False)
        embed.add_field(name="👑 " + lang.get_frase("utils.is_owner")[:-1],
                        value=owner)
        if icon is None:
            embed.set_thumbnail(file=disnake.File("logo.png"))
        else:
            embed.set_thumbnail(url=str(icon))
        await inter.response.send_message(embed=embed)

    @perms_check(["manage_roles"])
    @commands.slash_command()
    async def permissions(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
        emojies = EMOJI_ASSOCIATION
        lang = LangTool(inter.guild.id)
        member_perms = permsToDict(member.guild_permissions)
        # '❌|✅', 'permission translate', 'new line'
        embed_value = "".join(
            [f"{emojies[member_perms[perm]]} {lang.get_frase(f'permissions.{perm}')}\n" for perm in member_perms])
        embed = disnake.Embed(title=lang.get_frase("utils.members_permissions").format(member=member),
                              color=0x3ef0a9)
        embed.add_field(name=lang.get_frase("utils.perms_list"), value=embed_value)
        await inter.send(embed=embed, delete_after=30.0)
        print("успешно")

    @commands.slash_command()
    async def fetch_user(self, inter: disnake.ApplicationCommandInteraction, member):
        user = await self.client.fetch


def setup(client):
    client.add_cog(Utils(client))
