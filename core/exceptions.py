import disnake
from disnake.ext import commands


class NotEnoughPerms(commands.CheckFailure):
    def __init__(self, perms):
        self.permissions = perms
        super().__init__('NotEnoughPerms: Not enough permissions to execute the command')


class MemberHigherPermissions(commands.CheckFailure):
    def __init__(self):
        super().__init__('Member has higher permissions')


class NotGuildOwner(commands.CheckFailure):
    def __init__(self):
        super().__init__('Member is not owner this guild')


class NotDeveloper(commands.CheckFailure):
    def __init__(self):
        super().__init__('NotDeveloper: Member is not a developer of FlooryBot')


class InBlacklist(commands.CommandError):
    def __init__(self):
        super().__init__('InBlacklist: Member is blocked by bot developers')
