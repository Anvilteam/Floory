from cogs.main.main import Main


def setup(client):
    client.add_cog(Main(client))
