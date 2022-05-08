import core.database as database
from dataclasses import dataclass
from typing import Literal, Union


@dataclass
class GuildData:
    logging: Literal["true", "false"]
    logs_channel: Union[int, str]

    @classmethod
    async def from_cache(cls, guild_id) -> "GuildData":
        data = await database.redis_client.hgetall(guild_id)
        return cls(**data)


async def new_guild(guild_id: int):
    await database.cur("query", f"INSERT INTO guilds (guild) VALUES({guild_id});")
    data = ["false", "None"]
    await database.redis_client.hset(guild_id, "logging", data[0])
    await database.redis_client.hset(guild_id, "logs_channel", data[1])


async def refresh(guild_id: int, **kwargs):
    for k, v in kwargs.items():
        await database.redis_client.hset(guild_id, k, v)
