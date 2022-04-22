import disnake
from disnake.ext import commands

from loguru import logger

from core.tools import translated, COLORS, DEVELOPERS
from core.guild_data import new_guild, get_locale
from core.database import cur, redis_client
from core.exceptions import MemberHigherPermissions

__file__ = "cogs/events/locales"


@translated(__file__, "locales/main", "locales/exceptions", "locales/permissions")
class Events(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Guild):
        await new_guild(guild.id)
        logger.info(f"Новая гильдия! {guild.name}-{guild.id}")
        channel = guild.system_channel
        locale = "ru_RU"

        embed = disnake.Embed(title=self.lang[locale]["inviting_title"],
                              description=self.lang[locale]["inviting_description"],
                              color=COLORS['default'])
        embed.add_field(name=self.lang[locale]["faq1Q"], value=self.lang[locale]["faq1A"])
        embed.add_field(name=self.lang[locale]["faq2Q"], value=self.lang[locale]["faq2A"], inline=False)
        embed.add_field(name=self.lang[locale]["faq3Q"], value=self.lang[locale]["faq3A"], inline=False)
        if channel is not None:
            v = disnake.ui.View()
            v.add_item(disnake.ui.Button(label="Сервер поддержки", url="https://discord.gg/3KG3ue66rY"))
            await channel.send(embed=embed, view=v)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: disnake.Guild):
        await cur("query", f"DELETE FROM `guilds` WHERE `guild` = {guild.id};")
        await redis_client.delete(guild.id)
        logger.info(f"Бот покидает гильдию {guild.name}-{guild.id}")

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter: disnake.ApplicationCommandInteraction, error):
        locale = await get_locale(inter.guild.id)
        formatted = f"{error}|{inter.application_command.name}"
        embed = disnake.Embed(title=self.lang[locale]["error"],
                              color=COLORS["error"])
        if isinstance(error, commands.CommandOnCooldown):
            embed.add_field(name=f"```CommandOnCooldown```",
                            value=self.lang[locale]["CommandOnCooldown"].format(
                                time=f'{error.retry_after:.2f}{self.lang[locale]["second"]}'))

        elif isinstance(error, commands.MissingPermissions):
            permissions = error.missing_permissions
            embed_value = ''
            for perm in permissions:
                string = f"❌ {self.lang[locale][perm]}\n"
                embed_value += string
            embed.add_field(name=f"```NotEnoughPerms```",
                            value=self.lang[locale]["NotEnoughPerms"])
            embed.add_field(name="> Необходимые права", value=embed_value)

        elif isinstance(error, MemberHigherPermissions):
            embed.add_field(name=f"```MemberHigherPermissions```",
                            value=self.lang[locale]["MemberHigherPermissions"])
        elif isinstance(error, disnake.Forbidden):
            embed.add_field(name=f"```Forbidden```",
                            value=self.lang[locale]["Forbidden"])
        else:
            embed.description = formatted
            logger.error("-----------------Неизвестная ошибка!----------------")
            logger.error(formatted)
            logger.error(f"Гильдия {inter.guild}, пользователь {inter.author}")
            logger.error("----------------------------------------------------")
            bug_channel = await self.client.fetch_channel(967072415114993664)
            await bug_channel.send(f"загадка от жакак фреско:\n {formatted}\n"
                                   f"Гильдия {inter.guild}, пользователь {inter.author}")

        embed.set_thumbnail(file=disnake.File("logo.png"))
        embed.set_footer(text=self.lang[locale]["unknown"])
        v = disnake.ui.View()
        v.add_item(disnake.ui.Button(label="Сервер поддержки", url="https://discord.gg/3KG3ue66rY"))
        await inter.send(embed=embed, view=v)

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        locale = await get_locale(inter.guild.id)
        match inter.component.custom_id.split('-')[0]:
            case "vote":
                msg = inter.message
                embed = msg.embeds[0]
                fields = embed.fields
                button = inter.component
                view = disnake.ui.View.from_message(msg, timeout=None)
                # Разделям название варианта и кол-во проголосовавших
                label, counter = button.label.split('|')

                # Проверяем проголосовал ли юзер или нет
                votes = ''.join(map(lambda f: f.value, fields))
                variants = list(map(lambda f: f.name, fields))

                # Получаем индекс элемента за который проголосовали
                chosen_index = variants.index(label)
                field = fields[chosen_index]

                if inter.author.mention not in votes:
                    # Прибавляем 1 к счетчику на кнопке
                    view.children[chosen_index].label = label + f'|{int(counter) + 1}'
                    embed.set_field_at(chosen_index, name=field.name, value=field.value + f'\n{inter.author.mention}')
                    await inter.response.edit_message(embed=embed, view=view)
                else:
                    await inter.send(self.lang[locale]["alreadyVoted"], ephemeral=True)
            case "close_vote":
                if inter.author.guild_permissions.manage_messages:
                    msg = inter.message
                    embed = msg.embeds[0]
                    fields = embed.fields
                    fields_names = [f.name for f in fields]
                    button_list = msg.components[0].children
                    btns_counter = [button.label.split('|')[1] for button in button_list[:-1] if
                                    button.style != disnake.ButtonStyle.red]
                    for i in range(len(fields_names)):
                        embed.set_field_at(i, name=fields_names[i], value=btns_counter[i])
                    await inter.response.edit_message(content=self.lang[locale]['votingEnd'], embed=embed, components=[])
                else:
                    await inter.send(self.lang[locale]["nep"], ephemeral=True)
            case "idea":
                embed = inter.message.embeds[0]
                desc = embed.fields[0]
                supporters = embed.fields[1]
                view = disnake.ui.View.from_message(inter.message, timeout=None)
                if inter.author.mention not in supporters.value:
                    embed.clear_fields()
                    embed.add_field(name=desc.name, value=desc.value)
                    embed.add_field(name=supporters.name, value=supporters.value + f"\n{inter.author.mention}")
                    await inter.response.edit_message(view=view, embed=embed)
                else:
                    await inter.send("Вы уже поддержали данную идею", ephemeral=True)
            case "close_bug":
                if inter.author.id in DEVELOPERS:
                    await inter.response.defer()
                    await inter.delete_original_message()
                else:
                    await inter.send("Вы не разработчик!", ephemeral=True)
