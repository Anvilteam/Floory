import disnake
import random
import os
import yaml
import sys
import wavelink
from disnake.ext import commands, tasks

import core.database
from core.guild_data import new_guild
from core.database import cur, redis_client

from progress.bar import Bar
from loguru import logger

test_guilds = [737351356079145002,  # FallenSky
               906795717643882496,  # FlooryHome
               555376972990119964  # Polygon
               ]

# Настройки логирования
logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO",
           enqueue=True,
           backtrace=True,
           diagnose=True)
logger.add("logs/floory_{time}.log", enqueue=True)

# Загрузка конфигурации и клиента
with open('config.yaml', 'r', encoding="UTF-8") as f:
    cfg = yaml.safe_load(f)
logger.info(f"Запуск disnake {disnake.__version__}..")

client = commands.Bot(command_prefix=cfg["bot"]["prefix"], intents=disnake.Intents.all())


#                      test_guilds=test_guilds,
#                      sync_commands_debug=True,
#                      sync_permissions=True)


@client.event
async def on_ready():
    logger.info("Начало загрузки когов")
    for filename in os.listdir('./cogs'):
        if filename != '__pycache__':
            client.load_extension(f'cogs.{filename}')
            logger.info(f"Ког {filename} загружен")
    await wavelink.NodePool.create_node(bot=client,
                                        host='172.18.0.1',
                                        port=60002,
                                        password=cfg["lavalink"]["password"])
    logger.info("Успешная загрузка wavelink")
    logger.info("Начало загрузки кэша")
    await core.database.connect()
    await load_cache()
    await change_status.start()
    logger.info("Бот загружен!")


async def load_cache():
    with Bar('Загрузка кэша', max=len(client.guilds)) as bar:
        await redis_client.flushdb(True)
        for guild in client.guilds:
            data = await cur("fetchall", f"SELECT * FROM `guilds` WHERE `guild` = {guild.id}")
            if len(data) == 0:
                await new_guild(guild.id)
            else:
                await redis_client.hset(guild.id, "logging", data[1])
                await redis_client.hset(guild.id, "logs_channel", str(data[2]))
            bar.next()


@tasks.loop(seconds=300.0)
async def change_status():
    """Каждые 5 минут меняет статус"""
    current_status = random.choice(cfg["bot"]["splashes"])
    await client.change_presence(activity=disnake.Game(name=current_status, type=disnake.ActivityType.watching))


@tasks.loop(hours=1)
async def active_db():
    result = await cur("fetch" "SELECT logging FROM `guilds` WHERE `guild` = 555376972990119964")


client.run(cfg["bot"]["token"])
