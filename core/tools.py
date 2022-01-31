import time
import json
import disnake
from disnake.ext import commands
from core.exceptions import *
from core.database import get_guild


class LangTool:
    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.lang = self.get_guild_lang()

    def get_guild_lang(self):

        start = time.time()
        with open("core/cache.json", "r") as f2:
            data: dict = json.load(f2)
            if str(self.guild_id) in data.keys():
                lang = data[str(self.guild_id)]["lang"]
                end = time.time()
                print('[*] Время выполнения: {} секунд.'.format(end - start))
                return lang
            else:
                with open("core/cache.json", "w") as f2:
                    lang = get_guild(self.guild_id)["lang"]
                    data[self.guild_id] = {}
                    data[self.guild_id]["lang"] = lang
                    json.dump(data, f2)
                    end = time.time()
                    print('[*] Время выполнения: {} секунд.'.format(end - start))
                    return lang

    def get_frase(self, frase: str) -> str:
        category, frase = frase.split(".")
        lang = self.lang
        with open(f"locales/{lang}/{category}.json", "r", encoding='UTF-8') as f:
            data = json.load(f)
            return data[frase]


def perms_check(permissions: list = None):
    def predicate(inter):
        final_check = inter.author.top_role > inter.filled_options["member"].top_role
        if final_check:
            author_perms = inter.author.guild_permissions
            refreshed_ = permsToDict(author_perms)
            # iter(author_perms) -> (permission, value)
            missing_perms = [p for p in permissions if not refreshed_[p]]
            if len(missing_perms) != 0:
                raise NotEnoughPerms(missing_perms)
        else:
            raise MemberHigherPermissions

        return True
    return commands.check(predicate)


def permsToDict(perms: disnake.Permissions):
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
