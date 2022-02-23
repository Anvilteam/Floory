import disnake
import random
import os
import yaml
import logging
from disnake.ext import commands, tasks
from typing import List
import core.tools
from core.database import redis_client, cur
from core.views import *
from core.exceptions import *
from core.tools import LangTool, color_codes
from progress.bar import Bar

test_guilds = [737351356079145002,  # FallenSky
               906795717643882496  # FlooryHome
               ]
categories = ['moderation', 'utils', 'guild_config', 'fun']


async def autocomplete_categories(inter, string: str) -> List[str]:
    return [category for category in categories if string.lower() in category.lower()]


# Настройки логирования
logging.basicConfig(
    format='[%(asctime)s][%(levelname)s][%(name)s]: %(message)s',
    level=logging.INFO)

logger = logging.getLogger('floorybot')
logger.setLevel(logging.INFO)

# Загрузка конфигурации и клиента
cfg = yaml.safe_load(open('config.yaml', 'r', encoding="UTF-8"))
client = commands.Bot(command_prefix=cfg["bot"]["prefix"], intents=disnake.Intents.all())
# test_guilds=test_guilds,
# sync_commands_debug=True,
# sync_permissions=True)
logger.info("Инициализация команд и событий..")


def load_cache():
    with Bar('Загрузка кэша', max=len(client.guilds)) as bar:
        for guild in client.guilds:
            locale = cur("fetch", f"SELECT `locale` FROM `guilds` WHERE `guild` = {guild.id}")[0]
            redis_client.set(guild.id, locale)
            bar.next()


@client.event
async def on_ready():
    logger.info("Начало загрузки когов")
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
            logger.info(f"Ког {filename} загружен")
    logger.info("Начало загрузки кэша")
    load_cache()
    await change_status.start()
    logger.info("Бот загружен!")


@client.event
async def on_guild_join(guild: disnake.Guild):
    cur("query", f"INSERT INTO guilds (guild) VALUES({guild.id});")
    channel = guild.system_channel
    if channel is not None:
        embed = disnake.Embed(title="test")
        await channel.send(embed=embed)


@client.event
async def on_guild_remove(guild: disnake.Guild):
    cur("query", f"DELETE FROM `guilds` WHERE `guild` = {guild.id};")


@client.event
async def on_slash_command_error(inter, error: commands.CheckFailure):
    locale = LangTool(inter.guild.id)
    formatted = f"[{inter.guild.name}]|{error}"
    embed = disnake.Embed(title=locale["main.error"],
                          color=color_codes["error"])
    if isinstance(error, commands.CommandOnCooldown):
        embed.add_field(name=f"```CommandOnCooldown```",
                        value=locale["exceptions.CommandOnCooldown"].format(
                            time=f'{error.retry_after:.2f}{locale["main.second"]}'))
        embed.set_thumbnail(file=disnake.File("logo.png"))
        await inter.send(embed=embed, delete_after=30.0)
    logger.error(formatted)


@client.event
async def on_button_click(inter: disnake.MessageInteraction):
    match inter.component.custom_id.split('-')[0]:
        case 'voting':
            msg = inter.message
            embed = msg.embeds[0]
            fields = embed.fields
            button: disnake.ui.Button = inter.component
            label, counter = button.label.split('|')
            votes = ''
            for f in fields:
                votes += f.value
            fields_names = [f.name for f in fields]
            chosen_index = fields_names.index(label)
            field = fields[chosen_index]
            logger.info(label)
            if inter.author.mention not in votes:
                button.label = label + f'|{int(counter) + 1}'
                msg_components: list[disnake.ui.ActionRow] = msg.components
                button_list = msg_components[0].children
                button_list[chosen_index] = button
                action_row = disnake.ui.ActionRow()
                for btn in button_list:
                    action_row.add_button(label=btn.label, custom_id=btn.custom_id, style=btn.style)
                embed.set_field_at(chosen_index, name=field.name, value=field.value + f'\n{inter.author.mention}')
                await inter.response.edit_message(embed=embed, components=[action_row])
            else:
                await inter.send("а фиг тебе")
        case 'close_vote':
            locale = LangTool(inter.guild.id)
            msg = inter.message
            embed = msg.embeds[0]
            fields = embed.fields
            fields_names = [f.name for f in fields]
            msg_components: list[disnake.ui.ActionRow] = msg.components
            button_list = msg_components[0].children
            btns_counter = [button.label.split('|')[1] for button in button_list if button.style != disnake.ButtonStyle.red]
            for i in range(len(fields_names)):
                embed.set_field_at(i, name=fields_names[i], value=btns_counter[i])
            await inter.response.edit_message(content=locale['utils.votingEnd'], embed=embed, components=[])


@tasks.loop(seconds=120.0)
async def change_status():
    """Каждые 60 секунд меняет статус"""
    current_status = random.choice(cfg["bot"]["splashes"])
    await client.change_presence(activity=disnake.Activity(name=current_status, type=disnake.ActivityType.playing))


@client.slash_command()
async def about(inter: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(title="О боте")
    embed.add_field("Что такое FlooryBot?",
                    value="FlooryBot был придуман как open-source альтернатива другим бота для дискорда.\n"
                          "Бот содержит стандартные функции модерации, утилит и других полезных команд.\n"
                          "Стоит сказать, что состоит только из слэш команд, это необходимо для обеспечения меньшего кол-ва ошибок"
                          "в связи с человеческим фактором.\n"
                          "Если Вы хотите помочь в разработке или просто посмотреть на бота изнутри то ссылка на Github ниже")
    embed.add_field(name="Github", value="||https://github.com/Anvilteam/Floory||", inline=False)
    embed.add_field("P.S.", value="FlooryBot является дочерним проектом AnvilDev", inline=False)
    embed.set_thumbnail(file=disnake.File("logo.png"))
    await inter.send(embed=embed)


@client.slash_command(description="предложить идею для бота")
async def idea(inter: disnake.ApplicationCommandInteraction,
               title: str = commands.Param(description="Название идеи"),
               description: str = commands.Param(description="Подробное описание идеи")):
    channel = client.get_channel(944878540741025813)
    embed = disnake.Embed(title=title)
    embed.add_field(name="Описание", value=description)
    embed.add_field(name="Поддержали", value=f"{inter.author.mention}")
    embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
    view = Idea()
    msg = await channel.send(embed=embed, view=view)
    await msg.create_thread(name=title)
    await inter.send("Ваша идея была успешно предложена")


@client.slash_command(description="сообщить о баге/ошибке в боте")
async def bug(inter: disnake.ApplicationCommandInteraction,
              bug_name: str = commands.Param(description="Название бага"),
              bug_description: str = commands.Param(description="Подробное описание бага")):
    channel = client.get_channel(944979832092114997)
    embed = disnake.Embed(title="Баг " + bug_name)
    embed.add_field(name="Описание", value=bug_description)
    embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
    msg = await channel.send(embed=embed, view=CloseBugTicket())
    await msg.create_thread(name=bug_name)
    await inter.send("Баг был успешно отправлен", ephemeral=True)


@client.slash_command(description="список команд бота")
async def help(inter: disnake.ApplicationCommandInteraction,
               category: str = commands.Param(default=None, description='категория',
                                              autocomplete=autocomplete_categories)):
    embed = disnake.Embed(title="Help")


@client.slash_command(description="пинг бота")
async def ping(inter: disnake.ApplicationCommandInteraction):
    ping = client.latency
    await inter.response.send_message(f'Pong! {ping * 1000:.0f} ms')


@client.slash_command(description="тест вебхук")
async def webhook(inter: disnake.ApplicationCommandInteraction,
                  channel: disnake.TextChannel):
    await inter.channel.follow(destination=channel)
    await inter.send("тест")

client.run(cfg["bot"]["token"])
