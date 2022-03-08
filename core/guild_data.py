import core.database as database


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


async def get_locale(guild_id: int) -> int:
    locale = await database.redis_client.lrange(guild_id, 0, 0)
    return locale[0]

