from collections import OrderedDict
from time import time
from .queries import ANIME_QUERY, CHARACTER_QUERY, MANGA_QUERY

ANILIST_URL = "https://graphql.anilist.co"
CACHE_TTL = 300
CACHE_MAX = 32
_cache = OrderedDict()


def _cached(key):
    item = _cache.get(key)
    if item is None:
        return None
    stamp, value = item
    if time() - stamp > CACHE_TTL:
        _cache.pop(key, None)
        return None
    _cache.move_to_end(key)
    return value


def _store(key, value):
    if value is None:
        return None
    _cache[key] = (time(), value)
    _cache.move_to_end(key)
    while len(_cache) > CACHE_MAX:
        _cache.popitem(last=False)
    return value


async def _graphql(query, variables):
    from niquests import AsyncSession
    try:
        async with AsyncSession() as session:
            response = await session.post(
                ANILIST_URL,
                json={"query": query, "variables": variables},
                timeout=20,
            )
            if response.status_code != 200:
                return None
            payload = response.json()
    except Exception:
        return None
    if not isinstance(payload, dict) or payload.get("errors"):
        return None
    return payload.get("data")


async def fetch_anime(**variables):
    key = ("anime", variables.get("id"), variables.get("search"))
    hit = _cached(key)
    if hit is not None:
        return hit
    data = await _graphql(ANIME_QUERY, variables)
    return _store(key, (data or {}).get("Media"))


async def fetch_character(**variables):
    key = ("character", variables.get("id"), variables.get("search"))
    hit = _cached(key)
    if hit is not None:
        return hit
    data = await _graphql(CHARACTER_QUERY, variables)
    return _store(key, (data or {}).get("Character"))


async def fetch_manga(**variables):
    key = ("manga", variables.get("id"), variables.get("search"))
    hit = _cached(key)
    if hit is not None:
        return hit
    data = await _graphql(MANGA_QUERY, variables)
    return _store(key, (data or {}).get("Media"))
