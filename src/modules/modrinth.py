import functools
import requests
import shutil
import os

from threading import Thread
from typing import Literal, TypedDict, Callable

def worker(func):
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()

        return thread
    
    return wrapper

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

class ModrinthProjectQueried(TypedDict):
    project_id: str
    project_type: PROJECT_TYPE
    slug: str
    author: str
    title: str
    description: str
    categories: list[CATEGORIES_TYPE]
    display_categories: list[CATEGORIES_TYPE]
    versions: list[str]
    downloads: int
    follows: int
    icon_url: str
    date_created: str
    date_modified: str
    latest_version: str
    client_side: Literal["required", "unsopported", "optional"]
    server_side: Literal["required", "unsopported", "optional"]
    gallery: list[str]
    featured_gallery: str | None
    color: int

class ModrinthProjectFileHash(TypedDict):
    sha512: str
    sha1: str

class ModrinthProjectFile(TypedDict):
    hashes: ModrinthProjectFileHash
    url: str
    filename: str
    primary: bool
    size: int
    file_type: str | None

class ModrinthProjectDependency(TypedDict):
    version_id: str | None
    project_id: str
    file_name: str | None
    dependency_type: Literal["required", "optional"]

class ModrinthProject(TypedDict):
    game_versions: list[str]
    loaders: list[str]
    id: str
    project_id: str
    author_id: str
    featured: bool
    name: str
    version_number: str
    changelog: str
    changelog_url: str | None
    date_published: str
    downloads: int
    version_type: str
    status: str
    requested_status: str | None
    files: list[ModrinthProjectFile]
    dependencies: list

class ModrinthModQuery(TypedDict):
    hits: list[ModrinthProjectQueried]
    offset: int
    limit: int
    total_hits: int

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
    class UrlFileNotFound(Exception):
        pass

    def __init__(self) -> None:
        ...
    
    def get(self, *routes, **kwargs):
        formated_kwargs = [f"{x}={kwargs[x]}" for x in kwargs if kwargs[x] is not None]
        if len(routes) > 1:
            route = "/".join(routes)
        else:
            route = routes[0]

        print(f'https://api.modrinth.com/v2/{route}{"?" if len(formated_kwargs) > 0 else ""}{"&".join(formated_kwargs)}')
        return requests.get(f'https://api.modrinth.com/v2/{route}{"?" if len(formated_kwargs) > 0 else ""}{"&".join(formated_kwargs)}')
    
    def search_mods(self, query=None, filters: Filters={},
                    index: Literal["relevance","downloads","follows","newest","updated"]="relevance", 
                    offset=0, limit=10) -> tuple[ModrinthModQuery, Callable]:
        """Search mods

        Args:
            query (str, optional): The query to search for in modrinth. Defaults to None.
            filters (list, optional): The filters. Defaults to a empty list.
            index (str, optional): The sorting method. Defaults to "relevance".
            offset (int, optional): The offset into the search. Defaults to 0.
            limit (int, optional): The number of results returned by the search. Defaults to 10. Max value is 100.
        
        Returns:
            tuple[ModrinthModQuery, func]: Returns the query response and a function to get the next chunk of hits
        """
        
        def _next(limit=limit) -> tuple[ModrinthModQuery, Callable]:
            """Gets the next chunk of hits

            Returns:
                tuple[ModrinthModQuery, _next]: Returns the query response and a function to get the next chunk of hits
            """
            return self.search_mods(query=query, filters=filters, index=index, offset=limit, limit=limit)
            
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
        

        return (self.get("search", query=query, facets=stringify_list(_formated_filters), index=index, offset=offset, limit=limit).json(), _next)
    
    def get_project(self, project: ModrinthProjectQueried, version=None) -> list[ModrinthProject]:
        if version is not None:
            version = f'["{version}"]'

        return self.get("project", project["project_id"], "version?", game_versions=version).json()

    @worker
    def download_mod(self, mod: ModrinthProjectQueried, version: str, path: str, cb: dict[str, Callable[[int], None]]={}):
        proj_info = self.get_project(mod, version=version)
        
        proj_url = {}
        for x in proj_info:
            if "files" in x:
                for file in x["files"]:
                    proj_url["url"] = file["url"]
                    proj_url["name"] = file["filename"]
                    break

        if proj_url == "":
            raise self.UrlFileNotFound(f"Url file not found on mod {mod.get('title')}")
             
        with requests.get(proj_url["url"], stream=True) as r:
            r.raw.read = functools.partial(r.raw.read, decode_content=True)

            with open(os.path.join(path, proj_url["name"]), "wb") as file:

                length = r.headers.get("content-length")
                cb["setMax"](length)
                current = 0
                while True:
                    buf = r.raw.read(65536)
                    if not buf:
                        break
                    file.write(buf)
                    current += len(buf)
                    cb["update"](current)