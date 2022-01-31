import disnake
from disnake.ext import commands
from disnake.ext.commands import Param
from core.config import cCodes, EMOJI_ASSOCIATION
from core.tools import LangTool, permsToDict, perms_check
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
    async def logging(self, inter,
                      status: str = commands.Param(autocomplete=autocomplete_statuses)):
        await inter.send(f"Вы выбрали статус {status}")


def setup(client):
    client.add_cog(GuildConfig(client))
