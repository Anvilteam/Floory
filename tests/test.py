from enum import Enum


class RedisCache(Enum):
    guild_id = 0
    locale = 1
    logging = 2
    logs_channel = 3


print(getattr(RedisCache, 'locale').value)
