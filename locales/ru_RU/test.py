import disnake
import json

perms = disnake.Permissions()

with open("permissions.json", "r") as f:
    data = json.load(f)
    for i in perms:
        data[i[0]] = i[0]
    with open("permissions.json", "w") as f2:
        json.dump(data, f2)