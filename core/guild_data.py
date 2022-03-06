import database


class GuildData:
    def __init__(self, guild_id: int, locale: str = None, logging: str = None, log_channel: int = None):
        self.g_id = guild_id
        self.locale = locale
        self.logging = logging
        self.log_channel = log_channel

    async def set(self):
        data = database.redis_client


