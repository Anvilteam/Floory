import disnake
import core


class Idea(disnake.ui.View):
    def __init__(self):
        super().__init__()

    @disnake.ui.button(label="Поддерживаю", emoji='⭐', style=disnake.ButtonStyle.grey, custom_id='idea')
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

    @disnake.ui.button(label="Закрыть обсуждение", emoji='❌', style=disnake.ButtonStyle.grey, custom_id='bug')
    async def close(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author.id in core.tools.developers:
            await inter.response.defer()
            await inter.delete_original_message()
        else:
            await inter.send("Вы не разработчик!", ephemeral=True)


class SupportServer(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(label="Сервер бота", url="https://discord.gg/3KG3ue66rY"))
