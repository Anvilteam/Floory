import disnake
import random
import os
import yaml
import logging
from disnake.ext import commands, tasks
from core.database import redis_client, cur
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
client = commands.Bot(command_prefix=cfg["bot"]["prefix"], intents=disnake.Intents.all(),
                      test_guilds=test_guilds,
                      sync_commands_debug=True,
                      sync_permissions=True)
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


@tasks.loop(seconds=120.0)
async def change_status():
    """Каждые 60 секунд меняет статус"""
    current_status = random.choice(cfg["bot"]["splashes"])
    await client.change_presence(activity=disnake.Activity(name=current_status, type=disnake.ActivityType.playing))


@client.slash_command()
async def ping(inter: disnake.ApplicationCommandInteraction):
    ping = client.latency
    await inter.response.send_message(f'Pong! {ping * 1000:.0f} ms')


client.load_extension("jishaku")
client.run(cfg["bot"]["token"])