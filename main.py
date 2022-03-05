import disnake
import random
import os
import yaml
import core
import core.views
import sys
from disnake.ext import commands, tasks
from typing import List
from core.database import redis_client, cur
from core.exceptions import *
from core.tools import LangTool, color_codes
from progress.bar import Bar
from loguru import logger

test_guilds = [737351356079145002,  # FallenSky
               906795717643882496  # FlooryHome
               ]
categories = ['moderation', 'utils', 'guild_config', 'fun']


async def autocomplete_categories(inter, string: str) -> List[str]:
    return [category for category in categories if string.lower() in category.lower()]


# Настройки логирования
logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO",
           enqueue=True,
           backtrace=True,
           diagnose=True)
logger.add("logs/floory_{time}.log", enqueue=True)

# Загрузка конфигурации и клиента
cfg = yaml.safe_load(open('config.yaml', 'r', encoding="UTF-8"))
client = commands.Bot(command_prefix=cfg["bot"]["prefix"], intents=disnake.Intents.all())
# test_guilds=test_guilds,
# sync_commands_debug=True,
# sync_permissions=True)
logger.info("Запуск disnake..")


async def load_cache():
    with Bar('Загрузка кэша', max=len(client.guilds)) as bar:
        for guild in client.guilds:
            locale = await cur("fetch", f"SELECT `locale` FROM `guilds` WHERE `guild` = {guild.id}")
            redis_client.set(guild.id, locale)
            bar.next()


@client.event
async def on_ready():
    logger.info("Начало загрузки когов")
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
            logger.info(f"Ког {filename} загружен")
    logger.info("Начало загрузки кэша")
    await core.database.connect()
    await load_cache()
    await change_status.start()
    logger.info("Бот загружен!")


@client.event
async def on_guild_join(guild: disnake.Guild):
    await cur("query", f"INSERT INTO guilds (guild) VALUES({guild.id});")
    logger.info(f"Новая гильдия! {guild.name}-{guild.id}")
    channel = guild.system_channel
    locale = LangTool(guild.id)
    await locale.set()

    embed = disnake.Embed(title=locale["main.inviting_title"],
                          description=locale["main.inviting_description"],
                          color=color_codes['default'])
    embed.add_field(name=locale["main.faq1Q"], value=locale["main.faq1A"])
    embed.add_field(name=locale["main.faq2Q"], value=locale["main.faq2A"], inline=False)
    embed.add_field(name=locale["main.faq3Q"], value=locale["main.faq3A"], inline=False)
    if channel is not None:
        await channel.send(embed=embed, view=core.views.SupportServer())


@client.event
async def on_guild_remove(guild: disnake.Guild):
    await cur("query", f"DELETE FROM `guilds` WHERE `guild` = {guild.id};")
    logger.info(f"Бот покидает гильдию {guild.name}-{guild.id}")


@client.event
async def on_slash_command_error(inter: disnake.ApplicationCommandInteraction, error):
    locale = LangTool(inter.guild.id)
    await locale.set()
    formatted = f"{error}|{error.__traceback__}"
    embed = disnake.Embed(title=locale["main.error"],
                          color=color_codes["error"])
    if isinstance(error, commands.CommandOnCooldown):
        embed.add_field(name=f"```CommandOnCooldown```",
                        value=locale["exceptions.CommandOnCooldown"].format(
                            time=f'{error.retry_after:.2f}{locale["main.second"]}'))

    elif isinstance(error, NotEnoughPerms):
        permissions = error.permissions
        embed_value = ''
        for perm in permissions:
            string = f"❌ {locale[f'permissions.{perm}']}\n"
            embed_value += string
        embed.add_field(name=f"```NotEnoughPerms```",
                        value=locale["exceptions.NotEnoughPerms"])
        embed.add_field(name="> Необходимые права", value=embed_value)

    elif isinstance(error, MemberHigherPermissions):
        embed.add_field(name=f"```MemberHigherPermissions```",
                        value=locale["exceptions.MemberHigherPermissions"])
    elif isinstance(error, disnake.Forbidden):
        embed.add_field(name=f"```Forbidden```",
                        value=locale["exceptions.Forbidden"])
    else:
        logger.error("-----------------Неизвестная ошибка!----------------")
        logger.error(formatted)
        logger.error(f"Гильдия {inter.guild}, пользователь {inter.author}")
        logger.error("----------------------------------------------------")

    embed.set_thumbnail(file=disnake.File("logo.png"))
    embed.set_footer(text=locale["exceptions.unknown"])
    await inter.send(embed=embed, view=core.views.SupportServer())


@client.event
async def on_button_click(inter: disnake.MessageInteraction):
    locale = LangTool(inter.guild.id)
    await locale.set()
    match inter.component.custom_id.split('-')[0]:
        case 'voting':
            msg = inter.message
            embed = msg.embeds[0]
            fields = embed.fields
            button: disnake.ui.Button = inter.component
            # Разделям название варианта и кол-во проголосовавших
            label, counter = button.label.split('|')

            # Проверяем проголосовал ли юзер или нет
            votes = ''
            variants = []
            for f in fields:
                variants.append(f.name)
                votes += f.value

            # Получаем индекс элемента за который проголосовали
            chosen_index = variants.index(label)
            field = fields[chosen_index]

            logger.info(label)
            if inter.author.mention not in votes:
                # Прибавляем 1 к счетчику на кнопке
                button.label = label + f'|{int(counter) + 1}'
                # Обновляем кнопку
                button_list = msg.components[0].children
                button_list[chosen_index] = button
                new_btn_list = []
                for btn in button_list:
                    new_btn_list.append(disnake.ui.Button.from_component(btn))
                embed.set_field_at(chosen_index, name=field.name, value=field.value + f'\n{inter.author.mention}')
                await inter.response.edit_message(embed=embed, components=new_btn_list)
            else:
                await inter.send(locale["utils.alreadyVoted"], ephemeral=True)
        case 'close_vote':
            if inter.author.guild_permissions.manage_messages:
                locale = LangTool(inter.guild.id)
                await locale.set()
                msg = inter.message
                embed = msg.embeds[0]
                fields = embed.fields
                fields_names = [f.name for f in fields]
                button_list = msg.components[0].children
                btns_counter = [button.label.split('|')[1] for button in button_list if
                                button.style != disnake.ButtonStyle.red]
                for i in range(len(fields_names)):
                    embed.set_field_at(i, name=fields_names[i], value=btns_counter[i])
                await inter.response.edit_message(content=locale['utils.votingEnd'], embed=embed, components=[])
            else:
                await inter.send(locale["utils.nep"], ephemeral=True)


@tasks.loop(seconds=300.0)
async def change_status():
    """Каждые 5 минут меняет статус"""
    current_status = random.choice(cfg["bot"]["splashes"])
    await client.change_presence(activity=disnake.Game(name=current_status, type=disnake.ActivityType.watching))


@commands.cooldown(1, 180, commands.BucketType.member)
@client.slash_command(description="состояние бота")
async def status(inter: disnake.ApplicationCommandInteraction):
    splash = random.choice(cfg["bot"]["status_splashes"])
    locale = LangTool(inter.guild.id)
    await locale.set()
    latency = client.latency
    guilds = len(client.guilds)
    cmds = len(client.slash_commands)
    users = len(client.users)
    embed = disnake.Embed(title="FlooryBot",
                          description=f"```{latency * 1000:.0f} ms | {splash}```",
                          color=color_codes['default'])
    embed.add_field(name="🛡 " + locale["main.guilds"], value=f"```{guilds}```")
    embed.add_field(name="⚙ " + locale["main.cmds"], value=f"```{cmds}```", inline=False)
    embed.add_field(name="👥 " + locale["main.users"], value=f"```{users}```")
    embed.add_field(name="💻 " + locale["main.owners"], value=f"```Xemay#9586\nRedWolf#2007\nD3st0nλ#5637```",
                    inline=False)
    embed.add_field(name="<:github:945683293666439198> Github", value="[Тык](https://github.com/Anvilteam/Floory)")
    embed.add_field(name="🎲 Version", value="```0.3 beta```", inline=False)
    embed.set_thumbnail(file=disnake.File("logo.png"))
    await inter.send(embed=embed, view=core.views.SupportServer())


@commands.cooldown(1, 600, commands.BucketType.member)
@client.slash_command(description="предложить идею для бота")
async def idea(inter: disnake.ApplicationCommandInteraction,
               title: str = commands.Param(description="Название идеи"),
               description: str = commands.Param(description="Подробное описание идеи")):
    channel = client.get_channel(944878540741025813)
    embed = disnake.Embed(title=title)
    embed.add_field(name="Описание", value=description)
    embed.add_field(name="Поддержали", value=f"{inter.author.mention}")
    embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
    view = core.views.Idea()
    msg = await channel.send(embed=embed, view=view)
    await msg.create_thread(name=title)
    await inter.send("Ваша идея была успешно предложена")


@commands.cooldown(1, 600, commands.BucketType.member)
@client.slash_command(description="сообщить о баге/ошибке в боте")
async def bug(inter: disnake.ApplicationCommandInteraction,
              bug_name: str = commands.Param(description="Название бага"),
              bug_description: str = commands.Param(description="Подробное описание бага")):
    channel = client.get_channel(944979832092114997)
    embed = disnake.Embed(title="Баг " + bug_name)
    embed.add_field(name="Описание", value=bug_description)
    embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
    msg = await channel.send(embed=embed, view=core.views.CloseBugTicket())
    await msg.create_thread(name=bug_name)
    await inter.send("Баг был успешно отправлен", ephemeral=True)


@client.slash_command(description="список команд бота")
async def help(inter: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(title="📗 Help",
                          description="Здесь приведена `самая главная информация` о системе команд\n"
                                      "\n"
                                      "Единственное что надо запомнить, что у каждой категории команд есть свой префикс"
                                      " без которого Вы не сможете использовать команду, *его надо прописывать "
                                      "обязательно.*\n"
                                      "\n"
                                      "Здесь будут кратко описаны категории и их префиксы т.к. описание самих команд "
                                      "Вы увидете когда будете их писать.",
                          color=color_codes['default'])
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


@commands.cooldown(1, 45, commands.BucketType.member)
@client.slash_command(description="пинг бота")
async def ping(inter: disnake.ApplicationCommandInteraction):
    latency = client.latency
    await inter.response.send_message(f'Pong! {latency * 1000:.0f} ms')


client.run(cfg["bot"]["token"])
