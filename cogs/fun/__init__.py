from cogs.fun.fun import Fun


def setup(client):
    client.add_cog(Fun(client))
