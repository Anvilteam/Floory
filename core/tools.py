import json
import disnake
from disnake.ext import commands
from core.exceptions import *
from loguru import logger

from pathlib import Path

COLORS = {'default': 0x3ef0a9,
          'error': 0x3ef0a9}
BLACK_LIST = []
DEVELOPERS = (551439984255696908,
              # Xemay
              593079475453952000,
              # artior
              200243443467812864,
              # D3st0ny
              565172681532506131)


class Localization:
    def __init__(self, locale: dict):
        self.locale = locale

    def __getitem__(self, item: disnake.Locale) -> dict:
        if item in (disnake.Locale.ru,):
            return self.locale[item.__str__()]
        return self.locale["en_US"]


def is_higher():
    def predicate(inter: disnake.ApplicationCommandInteraction):
        check = inter.author.top_role > inter.filled_options["member"].top_role and inter.me.top_role > \
                inter.filled_options["member"].top_role
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


def dev_cooldown(msg: disnake.Message) -> commands.Cooldown:
    if msg.author.id in DEVELOPERS:
        return commands.Cooldown(1, 90)
    else:
        return commands.Cooldown(1, 30)


def news_status(webhooks: list[disnake.Webhook]) -> tuple:
    """Проверяет создан ли вебхук новостей на сервере"""

    news = None
    is_created = False
    for i in webhooks:
        if i.type == disnake.WebhookType.channel_follower and i.source_channel.id == 917015010801238037:
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
        multi_lang = {}
        for p in paths:
            folder = Path(p).resolve()

            for l in folder.iterdir():
                logger.info(f"Загрузка {l} для {cls.__qualname__ }")
                with open(l, "r", encoding='UTF-8') as f:
                    multi_lang[l.name[:-5]] = json.load(f)

            for k, v in multi_lang.items():
                if k not in translations.keys():
                    translations[k] = {}
                translations[k] = translations[k] | multi_lang[k]

        cls.lang = Localization(translations)
        return cls

    return wraps
