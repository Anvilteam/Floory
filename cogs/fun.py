import asyncio
import disnake
import random
import yaml
from disnake.ext import commands
from core.tools import LangTool

emojis = {1: 946031293655842856,
          2: 946031736196829195,
          3: 946031758565072896,
          4: 946031775405207603,
          5: 946031813544005642,
          6: 946031836637843476}

cfg = yaml.safe_load(open('config.yaml', 'r', encoding="UTF-8"))


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command()
    async def fun(self, inter):
        pass

    @fun.sub_command(description="подбросить монетку")
    @commands.cooldown(1, 25)
    async def coin(self, inter: disnake.ApplicationCommandInteraction):
        locale = LangTool(inter.guild.id)
        await locale.set()
        variants = ['орел', 'решка']
        coin_choice = random.choice(variants)
        await inter.response.send_message(locale["games.toss"])
        await asyncio.sleep(1)
        if coin_choice == "орел":
            await inter.edit_original_message(content=locale["fun.eagleWin"])
        else:
            await inter.edit_original_message(content=locale["fun.tailWin"])

    @fun.sub_command(description="подбросить кубики")
    async def dice(self, inter: disnake.ApplicationCommandInteraction,
                   amount: int = commands.Param(default=2, description="кол-во кубиков")):
        locale = LangTool(inter.guild.id)
        await locale.set()
        waiting = 0.5

        if amount < 3:
            await inter.send(locale["fun.tossingCubes"])
            for i in range(7):
                msg = ''
                for j in range(amount):
                    cube = random.randint(1, 6)
                    msg += f"<:die_{cube}:{emojis[cube]}> "
                await inter.edit_original_message(content=msg)
                await asyncio.sleep(waiting)
                waiting += 0.01
        elif 2 < amount < 10:
            if inter.guild.id != 906795717643882496:
                await inter.send(locale["fun.notHome"])
            else:
                await inter.send(locale["fun.tossingCubes"])
                for i in range(7):
                    msg = ''
                    for j in range(amount):
                        cube = random.randint(1, 6)
                        msg += f"<:die_{cube}:{emojis[cube]}> "
                    await inter.edit_original_message(content=msg)
                    await asyncio.sleep(waiting)
                    waiting += 0.01
        else:
            await inter.send(locale["fun.tmCubes"])

    @fun.sub_command(description="спросите магический шар о чём угодно")
    async def mystical_ball(self, inter: disnake.ApplicationCommandInteraction,
                            query: str = commands.Param(description="Ваш вопрос")):
        locale = LangTool(inter.guild.id)
        await locale.set()
        variant = ['main.true', 'main.false', 'fun.maybe']
        result = random.choice(variant)
        await inter.send(f"{inter.author} {locale['fun.asks']} {query} \n"
                         f"{locale['fun.answer']} {locale[result]}")


def setup(client):
    client.add_cog(Fun(client))
