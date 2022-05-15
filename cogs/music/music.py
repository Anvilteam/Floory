import disnake
import wavelink
import yaml
from disnake.ext import commands
from core.tools import is_bot_developer, COLORS
from core.exceptions import *
from loguru import logger


with open('config.yaml', 'r', encoding="UTF-8") as f:
    cfg = yaml.safe_load(f)

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.client.wait_until_ready()

        await wavelink.NodePool.create_node(bot=self.client,
                                            host='172.18.0.1',
                                            port=60002,
                                            password=cfg["lavalink"]["password"])
        logger.info("Успешная загрузка wavelink")

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
        yt = await wavelink.SearchableTrack.search(query)
        await player.play(yt)
