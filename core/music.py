import disnake
from disnake.ext import commands
import wavelink

from core.exceptions import NotInVoice, OtherVoice, EmptyQueue
from core.tools import translated, music_assert


@translated("locales/music")
class MusicView(disnake.ui.View):
    lang: dict[disnake.Locale, dict[str, str]]

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        return music_assert(interaction)

    async def on_error(self, error: Exception, item: disnake.ui.Item, interaction: disnake.MessageInteraction) -> None:
        if isinstance(error, NotInVoice):
            await interaction.send(self.lang[interaction.locale]["notInChannel"], ephemeral=True)
        elif isinstance(error, OtherVoice):
            await interaction.send(self.lang[interaction.locale]["otherChannel"], ephemeral=True)
        elif isinstance(error, EmptyQueue):
            await interaction.send(self.lang[interaction.locale]["emptyQueue"], ephemeral=True)

    @disnake.ui.button(emoji="⏸")
    async def pause(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        player: wavelink.Player = inter.guild.voice_client
        if player.is_playing():
            await player.pause()
            return
        lang = inter.locale
        await inter.send(self.lang[lang]["alreadyPaused"])

    @disnake.ui.button(emoji="▶")
    async def resume(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        player: wavelink.Player = inter.guild.voice_client
        if player.is_paused():
            await player.resume()
            return
        lang = inter.locale
        await inter.send(self.lang[lang]["alreadyResumed"])

    @disnake.ui.button(emoji="⏩")
    async def skip(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        player: wavelink.Player = inter.guild.voice_client
        if player.queue.count > 0:
            track = player.queue.pop()
            await player.play(track)
            await inter.send(f"Переключаю на {track.title}")
            return
        raise EmptyQueue
