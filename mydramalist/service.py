def _poster(value):
    return (value or "").replace("c.jpg?v=1", "f.jpg?v=1").strip()


def search_item(value):
    return {
        "title": value.get("title"),
        "year": value.get("year"),
        "slug": value.get("slug"),
        "thumbnail": _poster(value.get("poster")),
        "poster": _poster(value.get("poster")),
        "url": value.get("link") or value.get("url"),
    }


def drama(value):
    details = value.get("details") or {}
    others = value.get("others") or {}
    synopsis = value.get("synopsis") or ""
    poster = _poster(value.get("poster"))
    return {
        "title": value.get("title"),
        "native_title": others.get("native_title") or [],
        "also_known_as": value.get("also_known_as") or [],
        "slug": value.get("slug"),
        "url": value.get("link") or "",
        "thumbnail": poster,
        "poster": poster,
        "rating": value.get("rating"),
        "score": details.get("score"),
        "episodes": details.get("episodes"),
        "type": details.get("type"),
        "country": details.get("country"),
        "aired": details.get("aired"),
        "aired_on": details.get("aired_on"),
        "duration": details.get("duration"),
        "content_rating": details.get("content_rating"),
        "original_network": details.get("original_network"),
        "watchers": details.get("watchers"),
        "ranked": details.get("ranked"),
        "popularity": details.get("popularity"),
        "genres": others.get("genres") or [],
        "tags": others.get("tags") or [],
        "director": others.get("director") or [],
        "screenwriter": others.get("screenwriter") or [],
        "cast": value.get("casts") or [],
        "related_content": others.get("related_content") or [],
        "synopsis": synopsis,
    }
