import disnake
import core
import string
import random
from core.tools import LangTool


class Idea(disnake.ui.View):
    def __init__(self):
        super().__init__()

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
        super().__init__()

    @disnake.ui.button(label="Закрыть обсуждение", emoji='❌', style=disnake.ButtonStyle.grey)
    async def close(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author.id in core.tools.developers:
            await inter.response.defer()
            await inter.delete_original_message()
        else:
            await inter.send("Вы не разработчик!", ephemeral=True)


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
        self.locale = LangTool(locale)
        for i in range(variants_count):
            components.append(disnake.ui.TextInput(label=f"Вариант голосования {i}",
                                                   custom_id="".join(
                                                       random.choice(string.ascii_lowercase + string.digits) for _ in
                                                       range(4))))
        super().__init__(title="Голосование", components=components)

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        variants = interaction.text_values.values()
        view = disnake.ui.View()
        for var in variants:
            self.embed.add_field(name=var, value='-----')
            custom_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(int(4)))
            btn = disnake.ui.Button(label=var + '|0', custom_id=f'voting-{custom_id}-{interaction.id}')
            view.add_item(btn)
        view.add_item(disnake.ui.Button(label=self.locale["utils.closeVoting"], style=disnake.ButtonStyle.red,
                                        custom_id='close_vote', emoji='❌'))
        await interaction.send(embed=self.embed, view=view)



