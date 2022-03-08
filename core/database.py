import asyncio
import aiomysql
import loguru
import yaml
import aioredis
from loguru import logger

cfg = yaml.safe_load(open('config.yaml', 'r'))
loop = asyncio.get_event_loop()

redis_client = aioredis.from_url(url="redis://127.0.0.1", port=6379, db=0, decode_responses=True)


async def connect():
    global connection
    connection = await aiomysql.connect(host=cfg["mysql"]["host"],
                                        user=cfg["mysql"]["user"],
                                        password=cfg["mysql"]["password"],
                                        db=cfg["mysql"]["database"],
                                        autocommit=True)


@logger.catch
async def cur(_type, arg):
    result = None
    async with connection.cursor() as cur:
        match _type:
            case 'query':
                await cur.execute(arg)
            case 'fetch':
                await cur.execute(arg)
                result = await cur.fetchone()
            case 'fetchall':
                await cur.execute(arg)
                result = await cur.fetchall()
    if result is not None and len(result) == 1:
        result = result[0]
    if result is not None:
        return result
