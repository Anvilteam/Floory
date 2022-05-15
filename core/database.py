import asyncio
import aiomysql
import loguru
import yaml
import aioredis
from loguru import logger
from typing import Literal

with open('config.yaml', 'r', encoding="UTF-8") as f:
    cfg = yaml.safe_load(f)
loop = asyncio.get_event_loop()

redis_client = aioredis.from_url(url="redis://127.0.0.1", port=6379, db=0, decode_responses=True)


async def connect():
    global connection
    connection = await aiomysql.connect(host=cfg["mysql"]["host"],
                                        user=cfg["mysql"]["user"],
                                        password=cfg["mysql"]["password"],
                                        db=cfg["mysql"]["database"],
                                        autocommit=True)


def reconnect(func):
    def wrapper():
        try:
            func()
        except aiomysql.OperationalError:
            global connection
            await connection.close()
            logger.info("Соединение с бд закрыто")
            connection = await aiomysql.connect(host=cfg["mysql"]["host"],
                                                user=cfg["mysql"]["user"],
                                                password=cfg["mysql"]["password"],
                                                db=cfg["mysql"]["database"],
                                                autocommit=True)
            logger.info("Соединение с бд открыто\nВыполняю операцию еще раз")
            func()

    return wrapper


@reconnect
@logger.catch
async def cur(_type: Literal["query", "fetch", "fetchall"], arg: str):
    result = None
    async with connection.cursor() as cur_:
        match _type:
            case 'query':
                await cur_.execute(arg)
            case 'fetch':
                await cur_.execute(arg)
                result = await cur_.fetchone()
            case 'fetchall':
                await cur_.execute(arg)
                result = await cur_.fetchall()
    if result is not None and len(result) == 1:
        result = result[0]
    if result is not None:
        return result
