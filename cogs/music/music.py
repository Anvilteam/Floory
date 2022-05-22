import disnake
import wavelink
import yaml
from disnake.ext import commands

from core.checks import music_check
from core.tools import translated
from core.exceptions import NotInVoice, OtherVoice, EmptyQueue
from core.music import MusicView

with open('config.yaml', 'r', encoding="UTF-8") as f:
    cfg = yaml.safe_load(f)


@translated("locales/music")
class Music(commands.Cog):
    lang: dict[disnake.Locale, dict[str, str]]

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        if player.queue.count > 0 and reason != "REPLACED":
            track_ = player.queue.pop()
            await player.play(track_)

    @music_check()
    @commands.slash_command()
    async def music(self, inter):
        pass

    @music.error
    async def music_error(self, inter: disnake.ApplicationCommandInteraction, error: Exception):
        locale = inter.locale
        print(type(inter))
        if isinstance(error, NotInVoice):
            await inter.send(self.lang[locale]["notInChannel"], ephemeral=True)
        elif isinstance(error, OtherVoice):
            await inter.send(self.lang[locale]["otherChannel"], ephemeral=True)
        elif isinstance(error, EmptyQueue):
            await inter.send(self.lang[locale]["emptyQueue"], ephemeral=True)

    @music.sub_command(description="запустить музыку или добавить трек в очередь")
    async def play(self, inter: disnake.ApplicationCommandInteraction,
                   query: str = commands.Param(desc="запрос для поиска")):
        vc: disnake.VoiceState = inter.author.voice
        locale = inter.locale
        if len(query) > 40:
            await inter.send(self.lang[locale]["veryLongQuery"], ephemeral=True)
            return
        player: wavelink.Player = inter.guild.voice_client or await vc.channel.connect(cls=wavelink.Player)
        yt = await wavelink.YouTubeTrack.search(query=query)
        if len(yt) == 0:
            await inter.send(self.lang[locale]["noResults"], ephemeral=True)
            return
        yt = yt[0]
        embed = disnake.Embed(title=yt.title, description=f"{self.lang[locale]['author']} - {yt.author}")
        embed.set_thumbnail(yt.thumbnail)
        if player.queue.count > 0 or player.is_connected():
            if player.is_connected() and player.track is None:
                await player.play(yt)
                await inter.send(view=MusicView(), embed=embed)
                return
            inter.guild.voice_client.queue.put(yt)
            await inter.send(view=MusicView(), embed=disnake.Embed(
                title=self.lang[locale]["addedInQueue"],
                description=f"{self.lang[locale]['title']} - {yt.title}\n{self.lang[locale]['author']} - {yt.author}"
            ))
            return
        await player.play(yt)
        await inter.send(view=MusicView(), embed=embed)

    @commands.has_permissions(move_members=True)
    @commands.slash_command(description="отключить бота от голосового канала")
    async def disconnect(self, inter: disnake.ApplicationCommandInteraction):
        vc: wavelink.Player | None = inter.guild.voice_client
        if vc is not None:
            await vc.disconnect()
            await inter.send(self.lang[inter.locale]["disconnected"].format(member=inter.author))
            return
        await inter.send(self.lang[inter.locale]["notInChannel"])

    @music.sub_command(description="просмотреть очередь треков")
    async def queue_list(self, inter: disnake.ApplicationCommandInteraction):
        vc: disnake.VoiceState = inter.author.voice
        player: wavelink.Player = inter.guild.voice_client
        if player.queue.count == 0:
            await inter.send(self.lang[inter.locale]["emptyQueue"], ephemeral=True)
            return
        embed = disnake.Embed(title=self.lang[inter.locale]["queueList"], description="")
        for i in player.queue:
            embed.description = embed.description + f"\n{i.title}"
        await inter.send(embed=embed)

    @music.sub_command(description="удалить первый трек в очереди")
    async def queue_pop(self, inter: disnake.ApplicationCommandInteraction):
        vc: disnake.VoiceState = inter.author.voice
        player: wavelink.Player = inter.guild.voice_client
        if player.queue.count == 0:
            await inter.send(self.lang[inter.locale]["emptyQueue"], ephemeral=True)
            return
        track: wavelink.YouTubeTrack = player.queue.pop()
        embed = disnake.Embed(title=self.lang[inter.locale]["queuePop"].format(title=track.title))
        embed.set_thumbnail(track.thumbnail)
        await inter.send(embed=embed, view=MusicView())
