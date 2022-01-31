import disnake
import random
import time
from disnake.ext import commands
from core.tools import LangTool


class Games(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command()
    async def test(self, inter):
        print("subcmd test")


    @test.sub_command(description="тест")
    @commands.cooldown(1, 25)
    async def coin(self, inter: disnake.ApplicationCommandInteraction):
        lang = LangTool(inter.guild.id)
        variants = ['орел', 'решка']
        coin_choice = random.choice(variants)
        await inter.response.send_message(lang.get_frase("games.toss"))
        time.sleep(1.5)
        match coin_choice:
            case "орел":
                await inter.edit_original_message(content=lang.get_frase("games.eagleWin"))
            case _:
                await inter.edit_original_message(content=lang.get_frase("games.tailWin"))


def setup(client):
    client.add_cog(Games(client))
