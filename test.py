import disnake
import json

perms = disnake.Permissions()

with open("locales/permissions/ru_RU.json", "r") as f:
    data = json.load(f)
    for i in perms:
        data[i[0]] = i[0]
    with open("locales/permissions/ru_RU.json", "w") as f2:
        json.dump(data, f2)