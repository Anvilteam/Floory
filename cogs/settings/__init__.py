from cogs.settings.settings import Settings


def setup(client):
    client.add_cog(Settings(client))
