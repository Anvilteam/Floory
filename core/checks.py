import disnake
from disnake.ext import commands

from core.tools import music_assert, DEVELOPERS
from core.exceptions import NotGuildOwner, NotDeveloper, MemberHigherPermissions


def is_guild_owner():
    def predicate(inter: disnake.ApplicationCommandInteraction):
        check = inter.author == inter.guild.owner
        if not check:
            raise NotGuildOwner
        return True

    return commands.check(predicate)


def music_check():
    return commands.check(music_assert)


def is_bot_developer():
    def predicate(inter: disnake.ApplicationCommandInteraction):
        # Список id разработчиков бота
        if inter.author.id not in DEVELOPERS:
            raise NotDeveloper
        return True

    return commands.check(predicate)


def is_higher():
    def predicate(inter: disnake.ApplicationCommandInteraction):
        check = inter.author.top_role > inter.filled_options["member"].top_role and inter.me.top_role > \
                inter.filled_options["member"].top_role
        if not check:
            raise MemberHigherPermissions
        return True

    return commands.check(predicate)
