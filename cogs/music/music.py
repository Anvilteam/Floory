import disnake
import wavelink
import yaml
from disnake.ext import commands
from core.tools import is_bot_developer, COLORS
from core.exceptions import *
from loguru import logger
from core.music import MusicView

with open('config.yaml', 'r', encoding="UTF-8") as f:
    cfg = yaml.safe_load(f)


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        if player.queue.count > 0 and reason != "REPLACED":
            track_ = player.queue.pop()
            await player.play(track_)

    @commands.slash_command()
    async def music(self, inter):
        pass

    @music.sub_command()
    async def play(self, inter: disnake.ApplicationCommandInteraction,
                   query: str = commands.Param(desc="запрос для поиска")):
        vc: disnake.VoiceState = inter.author.voice
        if vc is None or vc.channel is None:
            await inter.send("Вы не в голосовом канале", ephemeral=True)
            return
        if len(query) >= 40:
            await inter.send("Запрос не может быть длиннее 40 символов", ephemeral=True)
            return
        if inter.guild.voice_client is not None and inter.guild.voice_client.channel != vc.channel:
            await inter.send("Бот уже в другом голосовом канале", ephemeral=True)
            return
        player: wavelink.Player = await vc.channel.connect(cls=wavelink.Player)
        yt = await wavelink.YouTubeTrack.search(query=query)
        if len(yt) == 0:
            await inter.send("По вашему запросу ничего не найдено", ephemeral=True)
            return
        yt = yt[0]
        if player.queue.count > 0:
            inter.guild.voice_client.queue.put(yt)
            await inter.send(view=MusicView(), embed=disnake.Embed(
                title=f"Трек добавлен в очередь", description=f"Название - {yt.title}\nАвтор - {yt.author}"
            ))
            return
        embed = disnake.Embed(title=yt.title,
                              description=f"Author - {yt.author}")
        embed.set_thumbnail(yt.thumbnail)
        await player.play(yt)
        await inter.send(view=MusicView(), embed=embed)

    @music.sub_command()
    async def queue_list(self, inter: disnake.ApplicationCommandInteraction):
        vc: disnake.VoiceState = inter.author.voice
        if vc is None or vc.channel is None:
            await inter.send("Вы не в голосовом канале", ephemeral=True)
            return
        player: wavelink.Player = inter.guild.voice_client
        if player.queue.count == 0:
            await inter.send("Очередь пуста", ephemeral=True)
            return
        embed = disnake.Embed(title="Список очереди", description="")
        for i in player.queue:
            embed.description = embed.description + f"\n{i.title}"
        await inter.send(embed=embed)

    @music.sub_command()
    async def queue_add(self, inter: disnake.ApplicationCommandInteraction,
                        query: str = commands.Param(desc="запрос для поиска")):
        vc: disnake.VoiceState = inter.author.voice
        if vc is None or vc.channel is None:
            await inter.send("Вы не в голосовом канале")
            return
        player: wavelink.Player = inter.guild.voice_client
        yt = await wavelink.YouTubeTrack.search(query=query, return_first=True)
        inter.guild.voice_client.queue.put(yt)

        await inter.send(player.queue[-1].title)
