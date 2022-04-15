from cogs.dev.dev import Dev


def setup(client):
    client.add_cog(Dev(client))
