import disnake
import random
import time
from disnake.ext import commands
from core.tools import LangTool


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command()
    async def fun(self, inter):
        pass

    @fun.sub_command()
    @commands.cooldown(1, 25)
    async def coin(self, inter: disnake.ApplicationCommandInteraction):
        lang = LangTool(inter.guild.id)
        variants = ['орел', 'решка']
        coin_choice = random.choice(variants)
        await inter.response.send_message(lang["games.toss"])
        time.sleep(1.5)
        if coin_choice == "орел":
            await inter.edit_original_message(content=lang["games.eagleWin"])
        else:
            await inter.edit_original_message(content=lang["games.tailWin"])


def setup(client):
    client.add_cog(Fun(client))
