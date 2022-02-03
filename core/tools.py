import json
from core.exceptions import *
from core.database import redis_client, cur

color_codes = {'default': 0x3ef0a9,
               'error': 0x3ef0a9}


class LangTool:
    def __init__(self, guild_id):
        self.guild_id = guild_id
        self._set_guild_lang()

    def __getitem__(self, key):
        category, frase = key.split(".")
        lang = self.locale
        with open(f"locales/{lang}/{category}.json", "r", encoding='UTF-8') as f:
            data = json.load(f)
            return data[frase]

    def _set_guild_lang(self):
        locale = str(redis_client.get(self.guild_id))[2:-1]
        if locale is not None:
            self.locale = locale
        locale = cur("fetch", f"SELECT `locale` FROM `guilds` WHERE `guild` = {self.guild_id}")
        self.locale = locale[0]


def has_permissions(permissions: list = None, position_check=True):
    def predicate(inter):
        check = True
        if position_check:
            check = inter.author.top_role > inter.filled_options["member"].top_role
        if check:
            author_perms: disnake.Permissions = inter.author.guild_permissions
            refreshed_: dict = modify_permissions(author_perms)
            # iter(author_perms) -> (permission, value)
            missing_perms = [p for p in permissions if not refreshed_[p]]
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
        developers = [551439984255696908]
        if inter.author.id not in developers:
            raise NotBotDeveloper
        return True

    return commands.check(predicate)


def modify_permissions(perms: disnake.Permissions) -> dict:
    permissions = {}
    for perm, value in perms:
        permissions[perm] = value
    return permissions


def benchmark(func):
    import time

    def wrapper():
        start = time.time()
        func()
        end = time.time()
        print('[*] Время выполнения: {} секунд.'.format(end - start))

    return wrapper
