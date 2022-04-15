import core.database as database

REDIS_ID = {'locale': 0,
            'logging': 1,
            'logs_channel': 2}


class GuildData:
    def __init__(self, guild_id: int):
        self.g_id = guild_id
        self.locale = None
        self.logging = None
        self.logs_channel = None

    async def set_all(self):
        data = await database.redis_client.lrange(self.g_id, 0, -1)
        data.reverse()
        self.locale = data[0]
        self.logging = data[1]
        self.logs_channel = data[2]


async def get_locale(guild_id: int) -> str:
    locale = await database.redis_client.lrange(guild_id, 0, -1)
    locale.reverse()
    return locale[0]


async def new_guild(guild_id: int):
    await database.cur("query", f"INSERT INTO guilds (guild) VALUES({guild_id});")
    data = ["ru_RU", "true", "None"]
    await database.redis_client.lpush(guild_id, data[0], data[1], data[2])


async def refresh(guild_id: int, **values):
    for k, v in values.items():
        await database.redis_client.lset(guild_id, REDIS_ID[k], v)
