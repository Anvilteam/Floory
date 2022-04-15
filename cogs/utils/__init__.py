from cogs.utils.utils import Utils


def setup(client):
    client.add_cog(Utils(client))
