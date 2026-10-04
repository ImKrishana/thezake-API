from collections import OrderedDict
from time import time
from urllib.parse import quote

API = "https://kuryana.vercel.app"
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


async def _get(path):
    from niquests import AsyncSession
    try:
        async with AsyncSession() as session:
            response = await session.get(f"{API}{path}", timeout=20)
            if response.status_code != 200:
                return None
            return response.json()
    except Exception:
        return None


async def search_dramas(title):
    key = ("search", title.strip().lower())
    hit = _cached(key)
    if hit is not None:
        return hit
    payload = await _get(f"/search/q/{quote(title.strip())}")
    results = (payload or {}).get("results", {}).get("dramas", [])
    return _store(key, results)


async def fetch_drama(slug):
    key = ("drama", slug)
    hit = _cached(key)
    if hit is not None:
        return hit
    payload = await _get(f"/id/{quote(slug.strip())}")
    data = (payload or {}).get("data")
    return _store(key, data)
