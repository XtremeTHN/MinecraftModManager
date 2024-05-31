from modules.modrinth import ModrinthMods
import json

mocs = ModrinthMods()

mods, _next = mocs.search_mods(filters={"versions":["1.19", "1.10"], "categories":["fabric","forge"]}, limit=1)
print(mocs.download_mod(mods["hits"][0], "1.19", ".", cb={
    "setMax": print,
    "update": print,
}))
