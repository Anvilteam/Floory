import string
import disnake
import random
from disnake.ext import commands
from disnake.ext.commands import Param

from core.tools import perms_to_dict, translated, dev_cooldown
from core.cooldown import DynamicCooldown

from gpytranslate import Translator

__file__ = "cogs/utils/locales"
cooldown = DynamicCooldown(1, 45)


@translated(__file__, "locales/permissions")
class Utils(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command()
    async def utils(self, inter):
        pass

    @commands.has_permissions(manage_messages=True)
    @commands.dynamic_cooldown(cooldown, commands.BucketType.member)
    @utils.sub_command(description="создать голосование")
    async def voting(self, inter: disnake.ApplicationCommandInteraction,
                     name: str = commands.Param(description="название голосования"),
                     description: str = commands.Param(desc="описание голосования"),
                     variants: str = commands.Param(desc="варианты голосов (через /)"),
                     image: disnake.Attachment = commands.Param(default=None, desc="картинка")):
        variants_ = list(filter(lambda e: e not in ("", " "), variants.split("/")))
        if 1 < len(variants_) < 5 and len(set(variants_)) == len(variants_):
            locale = inter.locale
            embed = disnake.Embed(title=name, description=description)
            if image is not None:
                embed.set_image(image.url)
            view = disnake.ui.View()
            for v in variants_:
                custom_id = (random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
                embed.add_field(name=v, value="-------------------")
                view.add_item(disnake.ui.Button(label=v + "|0",
                                                custom_id=f"vote-{custom_id}"))
            view.add_item(disnake.ui.Button(label=self.lang[locale]["closeVoting"], emoji="❌", custom_id="close_vote-"))
            await inter.send(embed=embed, view=view)
        else:
            await inter.send("Произошла ошибка. Убедитесь что аргументы соответствуют правилам.")

    @utils.sub_command(description="получение информации о пользователе")
    async def member(self, inter: disnake.ApplicationCommandInteraction,
                     member: disnake.Member = commands.Param(description='пользователь')):
        locale = inter.locale
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
        locale = inter.locale
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
    @commands.bot_has_permissions(manage_roles=True)
    @utils.sub_command(description="получение прав конкретного пользователя")
    async def permissions(self, inter: disnake.ApplicationCommandInteraction,
                          member: disnake.Member = commands.Param(description='пользователь')):
        emojies = {0: '❌', 1: '✅'}
        locale = inter.locale
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

    @commands.message_command(name="Перевести")
    async def translate(self, inter: disnake.ApplicationCommandInteraction):
        locale = inter.locale
        t = Translator()
        message = inter.target
        lang = await t.detect(message.content)
        phrase = await t.translate(text=message.content, targetlang=locale.value)
        await inter.send(f"{message.content} :flag_{lang.replace('en_US', 'gb').replace('en_UK', 'gb')}: -> {phrase.text}"
                         f" :flag_{locale.value.replace('en_US', 'gb').replace('en_UK', 'gb')}:")

    @commands.message_command(name="Перевести на английский")
    async def to_english(self, inter: disnake.ApplicationCommandInteraction):
        t = Translator()
        message = inter.target
        phrase = await t.translate(text=message.content, targetlang="en_US")
        await inter.send(f"{message.content} -> {phrase.text} :flag_gb:")

    @commands.bot_has_permissions(manage_emojis=True)
    @commands.has_permissions(manage_emojis=True)
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
