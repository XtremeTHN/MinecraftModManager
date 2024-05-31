from modules.modrinth import ModrinthMods
import json

mocs = ModrinthMods()
# print(mocs.get("search", facets='[["versions:1.14"]]').json())

mods, _next = mocs.search_mods(filters={"versions":["1.19", "1.10"], "categories":["fabric","forge"]})