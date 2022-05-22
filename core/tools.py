import json

import disnake
import wavelink
from disnake.ext import commands

from core.exceptions import NotInVoice, OtherVoice

from loguru import logger

from pathlib import Path

COLORS = {'default': 0x3ef0a9,
          'error': 0x3ef0a9}
BLACK_LIST: list[int] = []
DEVELOPERS: tuple[int, ...] = (551439984255696908,
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


def dev_cooldown(msg: disnake.Message) -> commands.Cooldown:
    if msg.author.id in DEVELOPERS:
        return commands.Cooldown(1, 90)
    else:
        return commands.Cooldown(1, 30)


def music_assert(inter: disnake.ApplicationCommandInteraction | disnake.MessageInteraction) -> bool:
    vc: disnake.VoiceState = inter.author.voice
    if vc is None or vc.channel is None:
        raise NotInVoice
    if inter.guild.voice_client is not None and inter.guild.voice_client.channel != vc.channel:
        raise OtherVoice
    return True


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


def translated(*paths):
    def wraps(cls: commands.Cog):
        translations: dict[str, dict[str, str]] = {}
        multi_lang = {}
        for p in paths:
            folder = Path(p).resolve()

            for l in folder.iterdir():
                logger.info(f"Загрузка {l} для {cls.__qualname__}")
                with open(l, "r", encoding='UTF-8') as f:
                    multi_lang[l.name[:-5]] = json.load(f)

            for k, v in multi_lang.items():
                if k not in translations.keys():
                    translations[k] = {}
                translations[k] = translations[k] | multi_lang[k]

        cls.lang = Localization(translations)
        return cls

    return wraps
