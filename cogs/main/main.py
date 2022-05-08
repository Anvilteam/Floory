import disnake
from disnake.ext import commands

import random
import yaml

from loguru import logger

from core.tools import translated, COLORS
from core.cooldown import DynamicCooldown

__file__ = "cogs/main/locales"
with open('config.yaml', 'r', encoding="UTF-8") as f:
    cfg = yaml.safe_load(f)


@translated(__file__)
class Main(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.dynamic_cooldown(DynamicCooldown(1, 30), commands.BucketType.member)
    @commands.slash_command(description="состояние бота")
    async def status(self,
                     inter: disnake.ApplicationCommandInteraction):
        splash = random.choice(cfg["bot"]["status_splashes"])
        locale = inter.locale
        latency = self.client.latency
        guilds = len(self.client.guilds)
        cmds = len(self.client.slash_commands)
        users = len(self.client.users)
        embed = disnake.Embed(title="FlooryBot",
                              description=f"```{latency * 1000:.0f} ms | {splash}```",
                              color=COLORS['default'])
        embed.add_field(name="🛡 " + self.lang[locale]["guilds"], value=f"```{guilds}```")
        embed.add_field(name="⚙ " + self.lang[locale]["cmds"], value=f"```{cmds}```", inline=False)
        embed.add_field(name="👥 " + self.lang[locale]["users"], value=f"```{users}```")
        embed.add_field(name="💻 " + self.lang[locale]["owners"], value=f"```Xemay#9586\nRedWolf#5064\nD3st0nλ#5637```",
                        inline=False)
        embed.add_field(name="<:github:945683293666439198> Github", value="[Тык](https://github.com/Anvilteam/Floory)")
        embed.add_field(name="🎲 Version", value="```0.4.1 beta```", inline=False)
        embed.set_thumbnail(file=disnake.File("logo.png"))
        v = disnake.ui.View()
        v.add_item(disnake.ui.Button(label="Сервер поддержки", url="https://discord.gg/3KG3ue66rY"))
        await inter.send(embed=embed, view=v)

    @commands.dynamic_cooldown(DynamicCooldown(1, 600), commands.BucketType.member)
    @commands.slash_command(description="предложить идею для бота")
    async def idea(self,
                   inter: disnake.ApplicationCommandInteraction,
                   title: str = commands.Param(description="Название идеи"),
                   description: str = commands.Param(description="Подробное описание идеи")):
        channel = self.client.get_channel(944878540741025813)
        embed = disnake.Embed(title=title)
        embed.add_field(name="Описание", value=description)
        embed.add_field(name="Поддержали", value=f"{inter.author.mention}")
        embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(emoji="⭐", label="Поддерживаю", custom_id=f"idea-{inter.id}"))
        msg = await channel.send(embed=embed, view=view)
        await msg.create_thread(name=title)
        await inter.send("Ваша идея была успешно предложена")

    @commands.dynamic_cooldown(DynamicCooldown(1, 600), commands.BucketType.member)
    @commands.slash_command(description="сообщить о баге/ошибке в боте")
    async def bug(self,
                  inter: disnake.ApplicationCommandInteraction,
                  bug_name: str = commands.Param(description="Название бага"),
                  bug_description: str = commands.Param(description="Подробное описание бага")):
        channel = self.client.get_channel(944979832092114997)
        embed = disnake.Embed(title="Баг " + bug_name)
        embed.add_field(name="Описание", value=bug_description)
        embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(emoji="❌", label="Закрыть баг", custom_id="close_bug-"))
        msg = await channel.send(embed=embed, view=view)
        await msg.create_thread(name=bug_name)
        await inter.send("Баг был успешно отправлен", ephemeral=True)

    @commands.dynamic_cooldown(DynamicCooldown(1, 20), commands.BucketType.member)
    @commands.slash_command(description="список команд бота")
    async def help(self,
                   inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(title="📗 Help",
                              description="Здесь приведена `самая главная информация` о системе команд\n"
                                          "\n"
                                          "Единственное что надо запомнить, что у каждой категории команд есть свой префикс"
                                          " без которого Вы не сможете использовать команду, *его надо прописывать "
                                          "обязательно.*\n"
                                          "\n"
                                          "Здесь будут кратко описаны категории и их префиксы т.к. описание самих команд "
                                          "Вы увидете когда будете их писать.",
                              color=COLORS['default'])
        embed.add_field(name="🛡 Модерация",
                        value="> Обычные команды модерации, не более\nПрефикс - `moderation`")
        embed.add_field(name="⚙ Настройки",
                        value="> Настройки бота\nПрефикс - `settings`",
                        inline=False)
        embed.add_field(name="🔎 Утилиты",
                        value="> Различные полезные инструменты\nПрефикс - `utils`",
                        inline=False)
        embed.add_field(name="🎮 Веселости",
                        value="> Различные мини-игры и другие штучки\nПрефикс - `fun`",
                        inline=False)
        await inter.send(embed=embed)

    @commands.dynamic_cooldown(DynamicCooldown(1, 45), commands.BucketType.member)
    @commands.slash_command(description="пинг бота")
    async def ping(self,
                   inter: disnake.ApplicationCommandInteraction):
        latency = self.client.latency
        await inter.response.send_message(f'Pong! {latency * 1000:.0f} ms')
