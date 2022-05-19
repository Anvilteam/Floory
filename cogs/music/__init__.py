from cogs.music.music import MusicView


def setup(client):
    client.add_cog(MusicView(client))