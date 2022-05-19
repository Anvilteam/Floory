import disnake
from disnake.ext import commands
import wavelink

from core.tools import translated


@translated("locales/music")
class MusicView(disnake.ui.View):

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        user: disnake.Member = interaction.author
        bot = interaction.me
        lang = interaction.locale
        if any([user.voice.channel is None,
                bot.voice.channel is None,
                interaction.guild.voice_client is None or user.voice.channel != interaction.guild.voice_client.channel,
                ]):
            embed = disnake.Embed(title=self.lang[lang]["error"],
                                  description=f"{self.lang[lang]['reason']}\n"
                                              f"⬥ {self.lang[lang]['notInChannel']}\n"
                                              f"⬥ {self.lang[lang]['otherChannel']}")
            await interaction.send(embed=embed)
        return True

    @disnake.ui.button(emoji="⏸")
    async def pause(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        player: wavelink.Player = inter.guild.voice_client
        if player.is_playing():
            await player.stop()
            return
        lang = inter.locale
        await inter.send(self.lang[lang]["alreadyPaused"])

    @disnake.ui.button(emoji="▶")
    async def resume(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        player: wavelink.Player = inter.guild.voice_client
        if not player.is_playing():
            await player.resume()
            return
        lang = inter.locale
        await inter.send(self.lang[lang]["alreadyResumed"])

    @disnake.ui.button(emoji="⏩")
    async def skip(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        player: wavelink.Player = inter.guild.voice_client
        await player.queue.pop()
        await player.play(player.queue.pop())
