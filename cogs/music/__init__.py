from cogs.music.music import Music


def setup(client):
    client.add_cog(Music(client))