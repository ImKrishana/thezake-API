def normalize(value):
    result = value.get("result") or {}
    images = value.get("images") or {}
    media_type = result.get("media_type")
    title = result.get("title") or result.get("name") or result.get("original_title") or result.get("original_name")
    release_date = result.get("release_date") or result.get("first_air_date") or ""
    posters = images.get("posters") or []
    backdrops = images.get("backdrops") or []
    return {
        "id": result.get("id"),
        "media_type": media_type,
        "title": title,
        "original_title": result.get("original_title") or result.get("original_name"),
        "release_date": release_date,
        "year": release_date[:4] if release_date else None,
        "thumbnail": posters[0] if posters else None,
        "poster": posters[0] if posters else None,
        "backdrop": backdrops[0] if backdrops else None,
        "posters": posters,
        "backdrops": backdrops,
        "logos": images.get("logos") or [],
        "overview": result.get("overview"),
        "original_language": result.get("original_language"),
        "adult": result.get("adult", False),
        "vote_average": result.get("vote_average"),
        "vote_count": result.get("vote_count"),
        "popularity": result.get("popularity"),
        "genre_ids": result.get("genre_ids") or [],
        "url": f"https://www.themoviedb.org/{media_type}/{result.get('id')}" if media_type and result.get("id") else None,
    }
