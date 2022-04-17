import disnake
from disnake.ext import commands

from loguru import logger

from core.tools import translated, COLORS
from core.guild_data import new_guild, get_locale
from core.database import cur, redis_client
from core.exceptions import MemberHigherPermissions
from core.views import SupportServer

__file__ = "cogs/events/locales"


@translated(__file__, "locales/main", "locales/exceptions", "locales/permissions")
class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Guild):
        await new_guild(guild.id)
        logger.info(f"Новая гильдия! {guild.name}-{guild.id}")
        channel = guild.system_channel
        locale = "ru_RU"

        embed = disnake.Embed(title=self.lang[locale]["inviting_title"],
                              description=self.lang[locale]["inviting_description"],
                              color=COLORS['default'])
        embed.add_field(name=self.lang[locale]["faq1Q"], value=self.lang[locale]["faq1A"])
        embed.add_field(name=self.lang[locale]["faq2Q"], value=self.lang[locale]["faq2A"], inline=False)
        embed.add_field(name=self.lang[locale]["faq3Q"], value=self.lang[locale]["faq3A"], inline=False)
        if channel is not None:
            await channel.send(embed=embed, view=SupportServer())

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: disnake.Guild):
        await cur("query", f"DELETE FROM `guilds` WHERE `guild` = {guild.id};")
        await redis_client.delete(guild.id)
        logger.info(f"Бот покидает гильдию {guild.name}-{guild.id}")

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter: disnake.ApplicationCommandInteraction, error):
        locale = await get_locale(inter.guild.id)
        formatted = f"{error}|{inter.application_command.name}"
        embed = disnake.Embed(title=self.lang[locale]["error"],
                              color=COLORS["error"])
        if isinstance(error, commands.CommandOnCooldown):
            embed.add_field(name=f"```CommandOnCooldown```",
                            value=self.lang[locale]["CommandOnCooldown"].format(
                                time=f'{error.retry_after:.2f}{self.lang[locale]["second"]}'))

        elif isinstance(error, commands.MissingPermissions):
            permissions = error.missing_permissions
            embed_value = ''
            for perm in permissions:
                string = f"❌ {self.lang[locale][perm]}\n"
                embed_value += string
            embed.add_field(name=f"```NotEnoughPerms```",
                            value=self.lang[locale]["NotEnoughPerms"])
            embed.add_field(name="> Необходимые права", value=embed_value)

        elif isinstance(error, MemberHigherPermissions):
            embed.add_field(name=f"```MemberHigherPermissions```",
                            value=self.lang[locale]["MemberHigherPermissions"])
        elif isinstance(error, disnake.Forbidden):
            embed.add_field(name=f"```Forbidden```",
                            value=self.lang[locale]["Forbidden"])
        else:
            embed.description = formatted
            logger.error("-----------------Неизвестная ошибка!----------------")
            logger.error(formatted)
            logger.error(f"Гильдия {inter.guild}, пользователь {inter.author}")
            logger.error("----------------------------------------------------")

        embed.set_thumbnail(file=disnake.File("logo.png"))
        embed.set_footer(text=self.lang[locale]["unknown"])
        await inter.send(embed=embed, view=SupportServer())
