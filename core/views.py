import disnake


class Idea(disnake.ui.View):
    def __init__(self):
        super().__init__()

    @disnake.ui.button(label="Поддерживаю", emoji='⭐', style=disnake.ButtonStyle.grey, custom_id='idea')
    async def support(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        pass


class CloseBugTicket(disnake.ui.View):
    def __init__(self):
        super().__init__()

    @disnake.ui.button(label="Закрыть обсуждение", emoji='❌', style=disnake.ButtonStyle.grey, custom_id='bug')
    async def close(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        pass
