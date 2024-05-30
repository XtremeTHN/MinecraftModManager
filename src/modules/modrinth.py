import requests
from typing import Literal, TypedDict, Any

PROJECT_TYPE = Literal[
    "mods", "plugins", "datapacks", 
    "shaders", "resourcepacks", "modpacks"
]

CATEGORIES_TYPE = list[Literal[
    "adventure", "cursed", "decoration",
    "economy", "equipment", "food",
    "game-mechanics", "library", "magic", 
    "management", "minigame", "mobs",
    "optimization", "social", "storage",
    "technology", "transportation", "utility",
    "world-generation", "fabric", "forge", 
    "neoforge", "quilt", "rift"
]]

class Filters(TypedDict):
    versions: list[str]
    project_type: PROJECT_TYPE
    categories: CATEGORIES_TYPE

class ModrinthProject(TypedDict):
    project_id: str
    project_type: PROJECT_TYPE
    slug: str
    author: str
    title: str
    description: str

class ModrinthModQuery(TypedDict):
    hits: list[ModrinthProject]

def stringify_list(_list):
    res = "["
    for index, value in enumerate(_list):
        suffix = ","
        if type(value) == list:
            value = stringify_list(value)
        else:
            value = f'"{value}"'
        if index == len(_list) - 1:
            suffix = ""
        res = f'{res}{value}{suffix}'
    
    return res + "]"

 
class ModrinthMods:
    def __init__(self) -> None:
        ...
    
    def get(self, route, **kwargs):
        formated_kwargs = [f"{x}={kwargs[x]}" for x in kwargs if kwargs[x] is not None]
        if type(route) == list:
            route = "/".join(route)
        print(f'https://api.modrinth.com/v2/{route}{"?" if len(formated_kwargs) > 0 else ""}{"&".join(formated_kwargs)}')
        return requests.get(f'https://api.modrinth.com/v2/{route}{"?" if len(formated_kwargs) > 0 else ""}{"&".join(formated_kwargs)}')
    
    def search_mods(self, query=None, filters: Filters={},
                    index: Literal["relevance","downloads","follows","newest","updated"]="relevance", 
                    offset=0, limit=10):
        """Search mods

        Args:
            query (str, optional): The query to search for in modrinth. Defaults to None.
            filters (list, optional): The filters. Defaults to a empty list.
            index (str, optional): The sorting method. Defaults to "relevance".
            offset (int, optional): The offset into the search. Defaults to 0.
            limit (int, optional): The number of results returned by the search. Defaults to 10. Max value is 100.
        """
        if limit > 100:
            raise ValueError("Limit should not be more than 100.")
        
        _formated_filters = []
        if filters.get("project_type") is not None:
            ...
        
        if filters.get("categories") is not None:
            for x in filters["categories"]:
                _formated_filters.append([f"categories:{x}"])

        if filters.get("versions") is not None:
            versions = []
            for x in filters["versions"]:
                versions.append(f"versions:{x}")
            _formated_filters.append(versions)

        if "client_side" in filters:
            raise NotImplementedError("Choose another filter pls")
        
        elif "server_side" in filters:
            raise NotImplementedError("Choose another filter pls")
        
        elif "open_source" in filters:
            raise NotImplementedError("Choose another filter pls")
        

        return self.get("search", query=query, facets=stringify_list(_formated_filters), index=index, offset=offset, limit=limit).json()