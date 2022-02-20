import json
from core.exceptions import *
from core.database import redis_client, cur
from typing import List

color_codes = {'default': 0x3ef0a9,
               'error': 0x3ef0a9}
bot_black_list = list()
developers = [551439984255696908]


class LangTool:
    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.__set_guild_lang()

    def __getitem__(self, key):
        category, frase = key.split(".")
        lang = self.locale
        with open(f"locales/{lang}/{category}.json", "r", encoding='UTF-8') as f:
            data = json.load(f)
            return data[frase]

    def __set_guild_lang(self):
        locale = redis_client.get(self.guild_id)
        if locale is not None:
            self.locale = locale.decode()
        else:
            locale = cur("fetch", f"SELECT `locale` FROM `guilds` WHERE `guild` = {self.guild_id}")
            self.locale = locale[0]


def has_permissions(*perms: str, position_check: bool = True):
    def predicate(inter):
        check = True
        if position_check:
            check = inter.author.top_role > inter.filled_options["member"].top_role
        if check:
            author_perms: dict = perms_to_dict(inter.author.guild_permissions)
            # iter(author_perms) -> (permission, value)
            missing_perms = [p for p in perms if not author_perms[p]]
            if len(missing_perms) != 0:
                raise NotEnoughPerms(missing_perms)
        else:
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
        if inter.author.id not in developers:
            raise NotDeveloper
        return True

    return commands.check(predicate)


def perms_to_dict(perms: disnake.Permissions) -> dict:
    """Превращает disnake.Permissions в словарь для удобной работы"""

    permissions = {}
    for perm, value in perms:
        permissions[perm] = value
    return permissions

def not_in_black_list():
    def predicate(inter):
        pass

def benchmark(func):
    import time

    def wrapper():
        start = time.time()
        func()
        end = time.time()
        print('[*] Время выполнения: {} секунд.'.format(end - start))

    return wrapper
