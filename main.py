import disnake
import random
import os
import yaml
import logging
from disnake.ext import commands, tasks

import core.tools
from core.database import redis_client, cur
from core.views import *
from core.exceptions import *
from core.tools import LangTool, color_codes
from progress.bar import Bar

test_guilds = [737351356079145002,  # FallenSky
               906795717643882496  # FlooryHome
               ]

# Настройки логирования
logging.basicConfig(
    format='[%(asctime)s][%(levelname)s][%(name)s]: %(message)s',
    level=logging.INFO)

logger = logging.getLogger('floorybot')
logger.setLevel(logging.DEBUG)

# Загрузка конфигурации и клиента
cfg = yaml.safe_load(open('config.yaml', 'r', encoding="UTF-8"))
client = commands.Bot(command_prefix=cfg["bot"]["prefix"], intents=disnake.Intents.all())
                      #test_guilds=test_guilds,
                      #sync_commands_debug=True,
                      #sync_permissions=True)
logger.info("Инициализация команд и событий..")


def load_cache():
    with Bar('Загрузка кэша', max=len(client.guilds)) as bar:
        for guild in client.guilds:
            locale = cur("fetch", f"SELECT `locale` FROM `guilds` WHERE `guild` = {guild.id}")[0]
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
    load_cache()
    await change_status.start()
    logger.info("Бот загружен!")


@client.event
async def on_guild_join(guild: disnake.Guild):
    cur("query", f"INSERT INTO guilds (guild) VALUES({guild.id});")
    channel = guild.system_channel
    if channel is not None:
        embed = disnake.Embed(title="test")
        await channel.send(embed=embed)


@client.event
async def on_guild_remove(guild: disnake.Guild):
    cur("query", f"DELETE FROM `guilds` WHERE `guild` = {guild.id};")


@client.event
async def on_slash_command_error(inter, error: commands.CheckFailure):
    locale = LangTool(inter.guild.id)
    formatted = f"[{inter.guild.name}]|{error}"
    embed = disnake.Embed(title=locale["main.error"],
                          color=color_codes["error"])
    if isinstance(error, commands.CommandOnCooldown):
        embed.add_field(name=f"```CommandOnCooldown```",
                        value=locale["exceptions.CommandOnCooldown"].format(
                            time=f'{error.retry_after:.2f}{locale["main.second"]}'))
        embed.set_thumbnail(file=disnake.File("logo.png"))
        await inter.send(embed=embed, delete_after=30.0)
    logger.error(formatted)


@client.event
async def on_button_click(inter: disnake.MessageInteraction):
    match inter.component.custom_id:
        case 'idea':
            embed = inter.message.embeds[0]
            desc = embed.fields[0]
            supporters = embed.fields[1]
            if inter.author.mention not in supporters.value:
                embed.clear_fields()
                embed.add_field(name=desc.name, value=desc.value)
                embed.add_field(name=supporters.name, value=supporters.value + f"\n{inter.author.mention}")
                await inter.response.edit_message(view=Idea(), embed=embed)
            else:
                await inter.send("Вы уже поддержали данную идею", ephemeral=True)
        case 'bug':
            if inter.author.id in core.tools.developers:
                await inter.response.defer()
                await inter.delete_original_message()
            else:
                await inter.send("Вы не разработчик!", ephemeral=True)


@tasks.loop(seconds=120.0)
async def change_status():
    """Каждые 60 секунд меняет статус"""
    current_status = random.choice(cfg["bot"]["splashes"])
    await client.change_presence(activity=disnake.Activity(name=current_status, type=disnake.ActivityType.playing))


@client.slash_command()
async def about(inter: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(title="О боте")
    embed.add_field("Что такое FlooryBot?",
                    value="FlooryBot был придуман как open-source альтернатива другим бота для дискорда.\n"
                          "Бот содержит стандартные функции модерации, утилит и других полезных команд.\n"
                          "Стоит сказать, что состоит только из слэш команд, это необходимо для обеспечения меньшего кол-ва ошибок"
                          "в связи с человеческим фактором.\n"
                          "Если Вы хотите помочь в разработке или просто посмотреть на бота изнутри то ссылка на Github ниже")
    embed.add_field(name="Github", value="||https://github.com/Anvilteam/Floory||", inline=False)
    embed.add_field("P.S.", value="FlooryBot является дочерним проектом AnvilDev", inline=False)
    embed.set_thumbnail(file=disnake.File("logo.png"))
    await inter.send(embed=embed)


@client.slash_command(description="предложить идею для бота")
async def idea(inter: disnake.ApplicationCommandInteraction,
               title: str = commands.Param(description="Название идеи"),
               description: str = commands.Param(description="Подробное описание идеи")):
    channel = client.get_channel(944878540741025813)
    embed = disnake.Embed(title=title)
    embed.add_field(name="Описание", value=description)
    embed.add_field(name="Поддержали", value=f"{inter.author.mention}")
    embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
    view = Idea()
    msg = await channel.send(embed=embed, view=view)
    await msg.create_thread(name=title)
    await inter.send("Ваша идея была успешно предложена")


@client.slash_command(description="сообщить о баге/ошибке в боте")
async def bug(inter: disnake.ApplicationCommandInteraction,
              bug_name: str = commands.Param(description="Название бага"),
              bug_description: str = commands.Param(description="Подробное описание бага")):
    channel = client.get_channel(944979832092114997)
    embed = disnake.Embed(title="Баг " + bug_name)
    embed.add_field(name="Описание", value=bug_description)
    embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
    msg = await channel.send(embed=embed, view=CloseBugTicket())
    await msg.create_thread(name=bug_name)
    await inter.send("Баг был успешно отправлен", ephemeral=True)


@commands.has_permissions(manage_nicknames=True)
@client.slash_command()
async def ping(inter: disnake.ApplicationCommandInteraction):
    ping = client.latency
    await inter.response.send_message(f'Pong! {ping * 1000:.0f} ms')


client.run(cfg["bot"]["token"])
