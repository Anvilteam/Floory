import disnake
from disnake.ext import commands
from disnake.ext.commands import Param
from core.tools import LangTool, modify_permissions, has_permissions
from core.database import cur
from typing import List

modules_status = ["on", "off"]


async def autocomplete_statuses(inter, string: str) -> List[str]:
    return [status for status in modules_status if string.lower() in status.lower()]


class GuildConfig(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command()
    async def config(self, inter):
        pass

    @config.sub_command()
    async def news(self, inter: disnake.ApplicationCommandInteraction,
                   status: str = commands.Param(autocomplete=autocomplete_statuses)):
        lang = LangTool(inter.guild.id)
        match status:
            case "on":
                news_channel = cur("fetch", f"SELECT `news-channel` FROM `guilds` WHERE `guild` = {inter.guild.id}")[0]
                print(type(news_channel))
                if news_channel is not None:
                    cur("query", f"UPDATE `guilds` SET `news` = 'true' WHERE `guild` = {inter.guild.id}")
                    await inter.send(lang.get_frase("guild_config.news_on"))
                else:
                    await inter.send(lang.get_frase("guild_config.news_channel_req"))
            case "off":
                cur("query", f"UPDATE `guilds` SET `news` = 'false' WHERE `guild` = {inter.guild.id}")
                await inter.send(lang.get_frase("guild_config.news_off"))
            case _:
                await inter.send(lang.get_frase("guild_config.invalid_arg"))

    @config.sub_command()
    async def set_news_channel(self, inter: disnake.ApplicationCommandInteraction):
        lang = LangTool(inter.guild.id)
        cur("query", f"UPDATE `guilds` SET `news-channel` = {inter.channel.id} WHERE `guild` = {inter.guild.id}")
        await inter.send(lang.get_frase("guild_config.set_news_channel"))


def setup(client):
    client.add_cog(GuildConfig(client))
