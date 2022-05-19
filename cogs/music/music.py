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

    @commands.slash_command()
    async def music(self, inter):
        pass

    @music.sub_command()
    async def play(self, inter: disnake.ApplicationCommandInteraction,
                   query: str = commands.Param(desc="запрос для поиска")):
        vc: disnake.VoiceState = inter.author.voice
        if vc is None or vc.channel is None:
            await inter.send("Вы не в голосовом канале")
            return
        player: wavelink.Player = inter.guild.voice_client or await vc.channel.connect(cls=wavelink.Player)
        yt = await wavelink.YouTubeTrack.search(query=query, return_first=True)
        embed = disnake.Embed(title=yt.title,
                              description=f"Author - {yt.author}")
        embed.set_thumbnail(yt.thumbnail)
        await player.play(yt)
        await inter.send(view=MusicView())

    @music.sub_command()
    async def queue_add(self, inter: disnake.ApplicationCommandInteraction,
                        query: str = commands.Param(desc="запрос для поиска")):
        vc: disnake.VoiceState = inter.author.voice
        if vc is None or vc.channel is None:
            await inter.send("Вы не в голосовом канале")
            return
        player: wavelink.Player = inter.guild.voice_client or await vc.channel.connect(cls=wavelink.Player)
        yt = await wavelink.YouTubeTrack.search(query=query, return_first=True)
        player.queue.put(yt)