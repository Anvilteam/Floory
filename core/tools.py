import functools
import json
import os
import pathlib

import disnake
from disnake.ext import commands
from core.exceptions import *
from core.database import redis_client, cur
from loguru import logger

from pathlib import Path

COLORS = {'default': 0x3ef0a9,
          'error': 0x3ef0a9}
BLACK_LIST = list()
DEVELOPERS = (551439984255696908,)


class LangTool:
    def __init__(self, locale):
        self._locale = locale

    def __getitem__(self, key) -> str:
        category, frase = key.split(".")
        with open(f"locales/{self._locale}/{category}.json", "r", encoding='UTF-8') as f:
            data = json.load(f)
            return data[frase]


def is_higher():
    def predicate(inter):
        check = inter.author.top_role > inter.filled_options["member"].top_role
        if not check:
            raise MemberHigherPermissions
        return True

    return commands.check(predicate)


def is_guild_owner():
    def predicate(inter):
        check = inter.author == inter.guild.owner
        if not check:
            raise NotGuildOwner
        return True

    return commands.check(predicate)


def is_bot_developer():
    def predicate(inter):
        # Список id разработчиков бота
        if inter.author.id not in DEVELOPERS:
            raise NotDeveloper
        return True

    return commands.check(predicate)


def news_status(webhooks: list[disnake.Webhook]) -> tuple:
    """Проверяет создан ли вебхук новостей на сервере"""

    news = None
    is_created = False
    for i in webhooks:
        if i.type == disnake.WebhookType.channel_follower and i.source_channel.id == 917017050495471648:
            is_created = True
            news = i
            break
    return is_created, news


def perms_to_dict(perms: disnake.Permissions) -> dict:
    """Превращает disnake.Permissions в словарь для удобной работы"""

    permissions = {perm: value for perm, value in perms}
    # iter(author_perms) -> (permission, value)
    return permissions


def not_in_black_list():
    def predicate(inter):
        pass


def translated(*paths):
    def wraps(cls: commands.Cog):
        translations = {}
        for p in paths:
            folder = Path(p).resolve()
            print(folder)
            multi_lang = {}
            for l in folder.iterdir():
                logger.info(f"Загрузка {l} для {cls.__cog_name__}")
                with open(l, "r", encoding='UTF-8') as f:
                    multi_lang[l.name[:-5]] = json.load(f)

            translations = translations | multi_lang
        cls.lang = translations
        return cls

    return wraps

