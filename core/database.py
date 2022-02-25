import asyncio
import aiomysql
import yaml
import redis

cfg = yaml.safe_load(open('config.yaml', 'r'))
loop = asyncio.get_event_loop()

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


async def cur(_type, arg):
    pool = await aiomysql.create_pool(host=cfg["mysql"]["host"],
                                      user=cfg["mysql"]["user"],
                                      password=cfg["mysql"]["password"],
                                      db=cfg["mysql"]["database"],
                                      autocommit=True)
    result = None
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            match _type:
                case 'query':
                    await cur.execute(arg)
                case 'fetch':
                    await cur.execute(arg)
                    result = await cur.fetchone()
                case 'fetchall':
                    await cur.execute(arg)
                    result = await cur.fetchall()
    pool.close()
    await pool.wait_closed()
    if len(result) == 1:
        result = result[0]
    if result is not None:
        return result
