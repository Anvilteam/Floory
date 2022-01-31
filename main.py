import disnake
import random
import os
import yaml
from core import config
from disnake.ext import tasks
from disnake.ext import commands
from core.database import cur

test_guild = [737351356079145002,# FallenSky
              906795717643882496 # FlooryHome
              ]

cfg = yaml.safe_load(open('config.yaml', 'r'))

client = commands.Bot(command_prefix=config.PREFIX, intents=disnake.Intents.all(), test_guilds=[737351356079145002])



@client.event
async def on_ready():
    print("Бот загружен")
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
            print(f"Ког {filename} загружен")
    change_status.start()



@client.event
async def on_guild_join(guild: disnake.Guild):
    await cur("query", "")
"""@client.event
async def on_message(message: disnake.Message):"""


@tasks.loop(seconds=120.0)
async def change_status():
    """Каждые 60 секунд меняет статус"""
    current_status = random.choice(config.SPLASHES)
    await client.change_presence(activity=disnake.Activity(name=current_status, type=disnake.ActivityType.playing))

@client.slash_command()
async def ping(inter: disnake.ApplicationCommandInteraction):
    ping = client.latency
    await inter.response.send_message(f'Pong! {ping * 1000:.0f} ms')
client.load_extension("jishaku")
client.run(config.TOKEN)
