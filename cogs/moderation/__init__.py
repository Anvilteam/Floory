from cogs.moderation.moderation import Moderation


def setup(client):
    client.add_cog(Moderation(client))
