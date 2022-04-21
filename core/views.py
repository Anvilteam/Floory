import disnake
import core
import string
import random
from core.tools import translated
from core.guild_data import get_locale


class Idea(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Поддерживаю", emoji='⭐', style=disnake.ButtonStyle.grey)
    async def support(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        embed = inter.message.embeds[0]
        desc = embed.fields[0]
        supporters = embed.fields[1]
        if inter.author.mention not in supporters.value:
            embed.clear_fields()
            embed.add_field(name=desc.name, value=desc.value)
            embed.add_field(name=supporters.name, value=supporters.value + f"\n{inter.author.mention}")
            await inter.response.edit_message(view=Idea(), embed=embed)
        else:
            await inter.send("Вы уже поддержали данную идею", ephemeral=True)


class CloseBugTicket(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Закрыть обсуждение", emoji='❌', style=disnake.ButtonStyle.grey)
    async def close(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author.id in core.tools.DEVELOPERS:
            await inter.response.defer()
            await inter.delete_original_message()
        else:
            await inter.send("Вы не разработчик!", ephemeral=True)


class VotingButton(disnake.ui.Button):
    def __init__(self, label, custom_id):
        super().__init__(style=disnake.ButtonStyle.grey,
                         label=label,
                         custom_id=custom_id)
        self.lang = {"ru_RU": "Вы уже проголосовали!"

        }

    async def callback(self, interaction: disnake.MessageInteraction):
        locale = await get_locale(interaction.guild.id)
        msg = interaction.message
        embed = msg.embeds[0]
        fields = embed.fields
        button = interaction.component
        view = disnake.ui.View.from_message(msg, timeout=None)
        # Разделям название варианта и кол-во проголосовавших
        label, counter = button.label.split('|')

        # Проверяем проголосовал ли юзер или нет
        votes = ''.join(map(lambda f: f.value, fields))
        variants = list(map(lambda f: f.name, fields))

        # Получаем индекс элемента за который проголосовали
        chosen_index = variants.index(label)
        field = fields[chosen_index]

        if interaction.author.mention not in votes:
            # Прибавляем 1 к счетчику на кнопке
            view.children[chosen_index].label = label + f'|{int(counter) + 1}'
            embed.set_field_at(chosen_index, name=field.name, value=field.value + f'\n{interaction.author.mention}')
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            await interaction.send(self.lang[locale]["alreadyVoted"], ephemeral=True)


class CloseVoting(disnake.ui.Button):
    def __init__(self, phrase: str):
        super().__init__(style=disnake.ButtonStyle.red,
                         label=phrase,
                         emoji='❌',
                         custom_id=''.join(
                             random.choice(string.ascii_lowercase + string.digits) for _ in range(4)))
        self.lang = {"ru_RU": {"votingEnd": "Голосование закончено",
                               "nep": "Не достаточно прав (управлять сообщениями)"},
                     "en_US": {}}

    async def callback(self, interaction: disnake.MessageInteraction):
        locale = await get_locale(interaction.guild.id)
        if interaction.author.guild_permissions.manage_messages:
            msg = interaction.message
            embed = msg.embeds[0]
            fields = embed.fields
            fields_names = [f.name for f in fields]
            button_list = msg.components[0].children
            btns_counter = [button.label.split('|')[1] for button in button_list if
                            button.style != disnake.ButtonStyle.red]
            for i in range(len(fields_names)):
                embed.set_field_at(i, name=fields_names[i], value=btns_counter[i])
            await interaction.response.edit_message(content=self.lang[locale]['votingEnd'], embed=embed, components=[])
        else:
            await interaction.send(self.lang[locale]["nep"], ephemeral=True)


class SupportServer(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(label="Сервер поддержки", url="https://discord.gg/3KG3ue66rY"))


class VotingModal(disnake.ui.Modal):
    def __init__(self, variants_count: int,
                 embed: disnake.Embed,
                 locale: str):
        components = []
        self.embed = embed
        self.lang = \
            {"ru_RU": {
                "invalidVars": "Варианты не должны повторяться!",
                "closeVoting": "Закрыть голосование"
            }

            }
        for i in range(variants_count):
            components.append(disnake.ui.TextInput(label=f"Вариант голосования {i + 1}",
                                                   custom_id="".join(
                                                       random.choice(string.ascii_lowercase + string.digits) for _ in
                                                       range(4))))
        super().__init__(title="Голосование", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        locale = await get_locale(interaction.guild.id)
        variants = interaction.text_values.values()
        if len(variants) != len(set(variants)):
            await interaction.send(self.lang[locale]["invalidVars"])
            return
        view = disnake.ui.View(timeout=None)
        for var in variants:
            self.embed.add_field(name=var, value='-----')
            custom_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))
            btn = VotingButton(label=var+"|0", custom_id=custom_id)
            view.add_item(btn)
        view.add_item(CloseVoting(self.lang[locale]["closeVoting"]))
        await interaction.send(embed=self.embed, view=view)
