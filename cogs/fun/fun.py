import asyncio
import disnake
import random
import yaml
from disnake.ext import commands
from core.tools import translated
from core.guild_data import get_locale
from loguru import logger

__file__ = "cogs/fun/locales"

emojis = {1: 946031293655842856,
          2: 946031736196829195,
          3: 946031758565072896,
          4: 946031775405207603,
          5: 946031813544005642,
          6: 946031836637843476}

cfg = yaml.safe_load(open('config.yaml', 'r', encoding="UTF-8"))


@translated(__file__, "locales/main")
class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 25, commands.BucketType.member)
    @commands.slash_command()
    async def fun(self, inter):
        pass

    @fun.sub_command(description="подбросить монетку")
    async def coin(self, inter: disnake.ApplicationCommandInteraction):
        guild_locale = await get_locale(inter.guild.id)
        variants = ['орел', 'решка']
        coin_choice = random.choice(variants)
        await inter.response.send_message(self.lang[guild_locale]["toss"])
        await asyncio.sleep(1)
        if coin_choice == "орел":
            await inter.edit_original_message(content=self.lang[guild_locale]["eagleWin"])
        else:
            await inter.edit_original_message(content=self.lang[guild_locale]["tailWin"])

    @fun.sub_command(description="подбросить кубики")
    async def dice(self, inter: disnake.ApplicationCommandInteraction,
                   amount: int = commands.Param(default=2, description="кол-во кубиков", lt=7)):
        guild_locale = await get_locale(inter.guild.id)
        waiting = 0.5

        await inter.send(self.lang[guild_locale]["tossingCubes"])
        for i in range(7):
            msg = ''
            for j in range(amount):
                cube = random.randint(1, 6)
                msg += f"<:die_{cube}:{emojis[cube]}> "
            await inter.edit_original_message(content=msg)
            await asyncio.sleep(waiting)
            waiting += 0.01

    @fun.sub_command(description="спросите магический шар о чём угодно")
    async def mystical_ball(self, inter: disnake.ApplicationCommandInteraction,
                            query: str = commands.Param(description="Ваш вопрос")):
        guild_locale = await get_locale(inter.guild.id)
        variant = ['true', 'false', 'maybe']
        result = random.choice(variant)
        embed = disnake.Embed(title=f"🔮 - {self.lang[guild_locale]['mystic_ball']}",
                              description=f"{inter.author} **{self.lang[guild_locale]['asks']}** {query}",
                              color=0x8614a3)
        embed.add_field(name=self.lang[guild_locale]['answer'],
                        value=self.lang[guild_locale][result])
        await inter.send(embed=embed)

    @fun.sub_command(description="получить рандомный эмодзи")
    async def random_emoji(self, inter: disnake.ApplicationCommandInteraction):
        emoji = random.choice(self.client.emojis)
        embed = disnake.Embed(title="Эмоджи")
        embed.add_field("Ссылочка", f"[клик]({emoji.url})")
        embed.set_image(emoji.url)
        await inter.send(embed=embed)

