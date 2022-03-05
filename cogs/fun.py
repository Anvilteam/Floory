import asyncio
import disnake
import random
import yaml
from disnake.ext import commands
from core.tools import LangTool
from loguru import logger

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

    @commands.cooldown(1, 25, commands.BucketType.member)
    @commands.slash_command()
    async def fun(self, inter):
        pass

    @fun.sub_command(description="подбросить монетку")
    async def coin(self, inter: disnake.ApplicationCommandInteraction):
        locale = LangTool(inter.guild.id)
        await locale.set()
        variants = ['орел', 'решка']
        coin_choice = random.choice(variants)
        await inter.response.send_message(locale["fun.toss"])
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

        if amount < 6:
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
        embed = disnake.Embed(title=f"🔮 - {locale['fun.mystic_ball']}",
                              description=f"{inter.author} **{locale['fun.asks']}** {query}",
                              color=0x8614a3)
        embed.add_field(name=locale['fun.answer'],
                        value=locale[result])
        await inter.send(embed=embed)


def setup(client):
    client.add_cog(Fun(client))
