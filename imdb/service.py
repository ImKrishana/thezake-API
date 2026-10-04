def _names(values):
    return [getattr(value, "name", str(value)) for value in (values or [])]


def _plot(value):
    plot = getattr(value, "plot", None)
    if plot:
        return plot
    for key in ("summaries", "synopses"):
        values = getattr(value, key, None)
        if values:
            return values[0]
    return ""


def _award_text(value):
    awards = getattr(value, "awards", None)
    if not awards:
        return ""
    wins = getattr(awards, "wins", 0) or 0
    nominations = getattr(awards, "nominations", 0) or 0
    return {"wins": wins, "nominations": nominations}


def title(value):
    imdb_id = str(getattr(value, "imdb_id", getattr(value, "id", "")))
    trailers = getattr(value, "trailers", None) or []
    box_office = getattr(value, "box_office", None) or {}
    return {
        "id": imdb_id,
        "imdb_id": f"tt{imdb_id.removeprefix('tt')}",
        "title": getattr(value, "title", ""),
        "localized_title": getattr(value, "title_localized", ""),
        "kind": getattr(value, "kind", ""),
        "year": getattr(value, "year", None),
        "end_year": getattr(value, "year_end", None),
        "thumbnail": getattr(value, "cover_url", ""),
        "poster": getattr(value, "cover_url", ""),
        "url": getattr(value, "url", ""),
        "rating": getattr(value, "rating", None),
        "votes": getattr(value, "votes", None),
        "metascore": getattr(value, "metacritic_rating", None),
        "runtime_minutes": getattr(value, "duration", None),
        "release_date": getattr(value, "release_date", None),
        "release_country": getattr(value, "release_country", None),
        "certificate": getattr(value, "certificate", None) or getattr(value, "mpaa", None),
        "genres": getattr(value, "genres", None) or [],
        "countries": getattr(value, "countries", None) or [],
        "languages": getattr(value, "languages_text", None) or [],
        "plot": _plot(value),
        "trailer": trailers[-1] if trailers else None,
        "directors": _names(getattr(value, "directors", None)),
        "writers": _names((getattr(value, "categories", None) or {}).get("writer")),
        "stars": _names(getattr(value, "stars", None)),
        "production_companies": [
            getattr(item, "name", str(item))
            for item in (getattr(value, "company_credits", None) or {}).get("production", [])
        ],
        "awards": _award_text(value),
        "box_office": box_office,
    }
