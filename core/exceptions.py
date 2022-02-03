import disnake
from disnake.ext import commands


class NotEnoughPerms(disnake.ext.commands.CommandInvokeError):
    def __init__(self, perms):
        self.permissions = perms

    def __str__(self):
        return 'Not enough permissions to execute the command'


class MemberHigherPermissions(disnake.ext.commands.CommandInvokeError):
    def __str__(self):
        return 'Member has higher permissions'


class NotGuildOwner(commands.CommandError):
    def __str__(self):
        return 'Member is not owner this guild'


class NotBotDeveloper(commands.CommandError):
    def __str__(self):
        return 'Member is not a developer of FlooryBot'
