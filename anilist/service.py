def _date(value):
    if not value or not any(value.values()):
        return None
    return value


def _title(value):
    value = value or {}
    return {
        "romaji": value.get("romaji"),
        "english": value.get("english"),
        "native": value.get("native"),
    }


def _relation(value):
    node = value.get("node") or {}
    return {
        "relation_type": value.get("relationType"),
        "id": node.get("id"),
        "title": _title(node.get("title")),
        "format": node.get("format"),
        "status": node.get("status"),
        "source": node.get("source"),
        "average_score": node.get("averageScore"),
        "site_url": node.get("siteUrl"),
    }


def _relations(value):
    return [_relation(item) for item in (value or {}).get("edges", [])]


def _studios(value):
    return [
        {"name": item.get("name"), "site_url": item.get("siteUrl")}
        for item in (value or {}).get("nodes", [])
    ]


def _characters(value):
    result = []
    for item in (value or {}).get("edges", []):
        node = item.get("node") or {}
        result.append({
            "role": item.get("role"),
            "id": node.get("id"),
            "name": node.get("name"),
            "site_url": node.get("siteUrl"),
            "image": (node.get("image") or {}).get("large"),
        })
    return result


def _reviews(value):
    result = []
    for item in (value or {}).get("nodes", []):
        result.append({
            "summary": item.get("summary"),
            "rating": item.get("rating"),
            "score": item.get("score"),
            "site_url": item.get("siteUrl"),
            "user": (item.get("user") or {}).get("name"),
        })
    return result


def anime(value):
    return {
        "id": value.get("id"),
        "title": _title(value.get("title")),
        "thumbnail": f"https://img.anili.st/media/{value.get('id')}" if value.get("id") else None,
        "mal_id": value.get("idMal"),
        "type": value.get("type"),
        "format": value.get("format"),
        "status": value.get("status"),
        "description": value.get("description"),
        "start_date": _date(value.get("startDate")),
        "end_date": _date(value.get("endDate")),
        "season": value.get("season"),
        "season_year": value.get("seasonYear"),
        "episodes": value.get("episodes"),
        "duration": value.get("duration"),
        "country_of_origin": value.get("countryOfOrigin"),
        "source": value.get("source"),
        "hashtag": value.get("hashtag"),
        "trailer": value.get("trailer"),
        "updated_at": value.get("updatedAt"),
        "cover_image": (value.get("coverImage") or {}).get("large"),
        "banner_image": value.get("bannerImage"),
        "genres": value.get("genres") or [],
        "synonyms": value.get("synonyms") or [],
        "average_score": value.get("averageScore"),
        "mean_score": value.get("meanScore"),
        "popularity": value.get("popularity"),
        "trending": value.get("trending"),
        "favourites": value.get("favourites"),
        "tags": value.get("tags") or [],
        "studios": _studios(value.get("studios")),
        "site_url": value.get("siteUrl"),
        "external_links": value.get("externalLinks") or [],
        "next_airing_episode": value.get("nextAiringEpisode"),
        "relations": _relations(value.get("relations")),
        "characters": _characters(value.get("characters")),
        "reviews": _reviews(value.get("reviews")),
    }


def manga(value):
    return {
        "id": value.get("id"),
        "mal_id": value.get("idMal"),
        "title": _title(value.get("title")),
        "type": value.get("type"),
        "format": value.get("format"),
        "status": value.get("status"),
        "description": value.get("description"),
        "start_date": _date(value.get("startDate")),
        "end_date": _date(value.get("endDate")),
        "chapters": value.get("chapters"),
        "volumes": value.get("volumes"),
        "country_of_origin": value.get("countryOfOrigin"),
        "source": value.get("source"),
        "updated_at": value.get("updatedAt"),
        "cover_image": (value.get("coverImage") or {}).get("large"),
        "banner_image": value.get("bannerImage"),
        "genres": value.get("genres") or [],
        "synonyms": value.get("synonyms") or [],
        "average_score": value.get("averageScore"),
        "mean_score": value.get("meanScore"),
        "popularity": value.get("popularity"),
        "favourites": value.get("favourites"),
        "tags": value.get("tags") or [],
        "site_url": value.get("siteUrl"),
        "external_links": value.get("externalLinks") or [],
        "relations": _relations(value.get("relations")),
    }


def character(value):
    return {
        "id": value.get("id"),
        "name": value.get("name") or {},
        "site_url": value.get("siteUrl"),
        "image": (value.get("image") or {}).get("large"),
        "description": value.get("description"),
    }
