from cogs.settings.settings import Settings


def setup(client):
    print(type(client))
    client.add_cog(Settings(client))
