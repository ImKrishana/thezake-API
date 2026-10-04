import asyncio
from collections import OrderedDict
from time import time
from imdbio import get_movie, search_title

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


def _title_item(value):
    return {
        "id": str(getattr(value, "imdb_id", getattr(value, "id", ""))),
        "imdb_id": getattr(value, "imdbId", "") or f"tt{getattr(value, 'imdb_id', '')}",
        "title": getattr(value, "title", ""),
        "year": getattr(value, "year", None),
        "kind": getattr(value, "kind", ""),
        "rating": getattr(value, "rating", None),
        "thumbnail": getattr(value, "cover_url", ""),
        "url": getattr(value, "url", ""),
    }


async def search_titles(query):
    key = ("search", query.strip().lower())
    hit = _cached(key)
    if hit is not None:
        return hit
    try:
        result = await asyncio.to_thread(search_title, query.strip())
        titles = [_title_item(item) for item in (result.titles if result else [])]
    except Exception:
        titles = []
    return _store(key, titles)


async def fetch_title(imdb_id):
    clean_id = str(imdb_id).strip().lower().removeprefix("tt")
    key = ("title", clean_id)
    hit = _cached(key)
    if hit is not None:
        return hit
    try:
        value = await asyncio.to_thread(get_movie, clean_id)
    except Exception:
        value = None
    return _store(key, value)
