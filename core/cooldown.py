import disnake
from disnake import interactions
from disnake.ext import commands

from core.tools import DEVELOPERS


class DynamicCooldown:
    def __init__(self, rate: int, per: int):
        self.rate = rate
        self.per = per

    def __call__(self, inter: interactions.application_command.ApplicationCommandInteraction) -> commands.Cooldown:
        if inter.author.id in DEVELOPERS:
            return commands.Cooldown(1, 15)
        return commands.Cooldown(self.rate, self.per)
