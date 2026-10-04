import re
from collections import OrderedDict
from time import time

BASE = "https://tmdbapi.the-zake.workers.dev/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/"
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


def _normalize(value):
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def _year_query(query):
    text = query.strip()
    match = re.search(r"(19|20)\d{2}$", text)
    if not match:
        return text, None
    return text[: match.start()].strip(), match.group(0)


def _score(item, query, year):
    title = item.get("title") or item.get("name") or item.get("original_title") or item.get("original_name") or ""
    normalized_query = _normalize(query)
    normalized_title = _normalize(title)
    release = item.get("release_date") or item.get("first_air_date") or ""
    item_year = release[:4]
    vote_count = item.get("vote_count", 0) or 0
    popularity = item.get("popularity", 0) or 0
    score = 0
    if len(normalized_query) <= 3:
        score += 1000 if normalized_title == normalized_query else 500 if normalized_query in normalized_title else 0
    elif normalized_title == normalized_query:
        score += 4000
    elif normalized_title.startswith(normalized_query):
        score += 2500
    elif normalized_query in normalized_title:
        score += 1500
    if year and item_year == year:
        score += 5000
    return score + vote_count * 2 + popularity * 10


async def _get(path, params=None):
    from niquests import AsyncSession
    try:
        async with AsyncSession() as session:
            response = await session.get(
                f"{BASE}{path}",
                params=params or {},
                headers={"accept": "application/json"},
                timeout=45,
            )
            if response.status_code != 200:
                return None
            return response.json()
    except Exception:
        return None


async def search_title(query):
    text, year = _year_query(query)
    if not text:
        return None
    key = ("search", text.lower(), year)
    hit = _cached(key)
    if hit is not None:
        return hit
    payload = await _get("/search/multi", {
        "query": text,
        "include_adult": "false",
        "language": "en-US",
        "page": 1,
    })
    results = [item for item in (payload or {}).get("results", []) if item.get("media_type") in ("movie", "tv")]
    if year:
        filtered = [item for item in results if (item.get("release_date") or item.get("first_air_date") or "")[:4] == year]
        if filtered:
            results = filtered
    if not results:
        return None
    selected = max(results, key=lambda item: _score(item, text, year))
    return _store(key, selected)


def _pick_sets(items):
    groups = {"en": [], "other": [], "none": []}
    for item in items or []:
        language = item.get("iso_639_1")
        if language == "en":
            groups["en"].append(item)
        elif language in (None, "", "xx"):
            groups["none"].append(item)
        else:
            groups["other"].append(item)
    for group in groups.values():
        group.sort(key=lambda item: item.get("vote_count", 0), reverse=True)
    return groups["en"] or groups["other"] or groups["none"]


async def fetch_images(media_type, media_id):
    key = ("images", media_type, media_id)
    hit = _cached(key)
    if hit is not None:
        return hit
    path = f"/{'tv' if media_type == 'tv' else 'movie'}/{media_id}/images"
    params = {"include_image_language": "en,null,hi,ta,te,ml,kn,bn,mr,gu,pa,ur,fr,es,de,it,ja,ko,zh"}
    payload = await _get(path, params)
    payload = payload or {}
    backdrops = [item for item in payload.get("backdrops", []) if item.get("aspect_ratio", 0) >= 1.6]
    result = {
        "posters": [IMAGE_BASE + "w500" + item["file_path"] for item in _pick_sets(payload.get("posters"))[:10] if item.get("file_path")],
        "backdrops": [IMAGE_BASE + "original" + item["file_path"] for item in _pick_sets(backdrops)[:10] if item.get("file_path")],
        "logos": [IMAGE_BASE + "w500" + item["file_path"] for item in _pick_sets(payload.get("logos"))[:10] if item.get("file_path")],
    }
    return _store(key, result)


async def resolve(query):
    result = await search_title(query)
    if not result or not result.get("id"):
        return None
    images = await fetch_images(result["media_type"], result["id"])
    return {"result": result, "images": images}
