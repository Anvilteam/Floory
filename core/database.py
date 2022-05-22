import asyncio
import aiomysql
import loguru
import pymysql.err
import yaml
import aioredis
from loguru import logger
from typing import Literal, Union, Any
import functools

with open('config.yaml', 'r', encoding="UTF-8") as f:
    cfg = yaml.safe_load(f)
loop = asyncio.get_event_loop()

redis_client = aioredis.from_url(url=cfg["redis"]["host"], port=cfg["redis"]["port"], db=0, decode_responses=True)


async def connect() -> None:
    global connection
    connection = await aiomysql.connect(host=cfg["mysql"]["host"],
                                        user=cfg["mysql"]["user"],
                                        password=cfg["mysql"]["password"],
                                        db=cfg["mysql"]["database"],
                                        autocommit=True)


def reconnect():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except pymysql.err.OperationalError:
                global connection
                await connection.close()
                logger.info("Соединение с бд закрыто")
                connection = await aiomysql.connect(host=cfg["mysql"]["host"],
                                                    user=cfg["mysql"]["user"],
                                                    password=cfg["mysql"]["password"],
                                                    db=cfg["mysql"]["database"],
                                                    autocommit=True)
                logger.info("Соединение с бд открыто\nВыполняю операцию еще раз")
                return await func(*args, **kwargs)

        return wrapped

    return wrapper


@reconnect()
@logger.catch
async def cur(_type: Literal["query", "fetch", "fetchall"], arg: str) -> Union[int, str, bool] | tuple[Any]:
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
    return result
