import json
import disnake
from guild_data import GuildData
from core.exceptions import *
from core.database import redis_client, cur


color_codes = {'default': 0x3ef0a9,
               'error': 0x3ef0a9}
bot_black_list = list()
developers = [551439984255696908]


class LangTool:
    def __init__(self, locale):
        self._locale = locale

    def __getitem__(self, key) -> str:
        category, frase = key.split(".")
        with open(f"locales/{self._locale}/{category}.json", "r", encoding='UTF-8') as f:
            data = json.load(f)
            return data[frase]


def has_permissions(*perms: str, position_check: bool = True):
    def predicate(inter):
        check = True
        if position_check:
            check = inter.author.top_role > inter.filled_options["member"].top_role
        if check:
            author_perms: dict = perms_to_dict(inter.author.guild_permissions)

            def check(p):
                return not author_perms[p]

            missing_perms = list(filter(check, perms))
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

    permissions = {}
    # iter(author_perms) -> (permission, value)
    for perm, value in perms:
        permissions[perm] = value
    return permissions


def not_in_black_list():
    def predicate(inter):
        pass
