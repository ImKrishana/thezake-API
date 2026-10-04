import base64
import inspect
import json
from functools import lru_cache
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, Response
from anilist import *
from imdb import *
from mydramalist import *
from tmdb import *
from bypass.DDL import *
from platforms import *
from posters import *

app = FastAPI(
    title="TheZake",
    docs_url=None,
    redoc_url=None,
)


@app.middleware("http")
async def m3(request, call_next):
    response = await call_next(request)
    if request.url.path == "/poster" or request.url.path.startswith("/posters/"):
        return response
    if "application/json" not in response.headers.get("content-type", ""):
        return response
    body = b"".join([chunk async for chunk in response.body_iterator])
    try:
        payload = json.loads(body)
    except (TypeError, ValueError):
        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type="application/json",
        )
    if isinstance(payload, dict):
        payload.setdefault("credits", r8())
    headers = dict(response.headers)
    headers.pop("content-length", None)
    return JSONResponse(
        content=payload,
        status_code=response.status_code,
        headers=headers,
    )

for router in poster_routers:
    app.include_router(
        router,
        prefix="/posters",
        tags=["Posters"],
    )


def build_poster_handlers():
    handlers = {}
    for router in poster_routers:
        for route in router.routes:
            path = getattr(route, "path", "")
            endpoint = getattr(route, "endpoint", None)
            if path.startswith("/") and endpoint:
                handlers[path.removeprefix("/")] = endpoint
    return handlers

poster_handlers = build_poster_handlers()
z1 = "ttJyNGGwUbCICASkGelYLgABhqCAAAAAAGrBXmA4Be-F85ltI5jCyNTnVhChbIRqUzIhqn"
k7 = "Zake"

@lru_cache(maxsize=1)
def r8():
    packed = base64.urlsafe_b64decode((z1 + m6 + n4).encode())
    salt = packed[:16]
    iterations = int.from_bytes(packed[16:20], "big")
    encrypted = base64.urlsafe_b64encode(packed[20:])
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.fernet import Fernet
    key = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend(),
    ).derive((k7 + q2 + p8).encode())
    return json.loads(Fernet(base64.urlsafe_b64encode(key)).decrypt(encrypted))


async def invoke_poster_handler(handler, url):
    result = handler(url=url)
    if inspect.isawaitable(result):
        result = await result

    if isinstance(result, Response):
        body = result.body or b"{}"
        payload = json.loads(body.decode("utf-8"))
        return payload, result.status_code

    return result, 200


@app.get("/poster", tags=["Posters"])
async def poster(url: str = Query(..., description="Supported platform content URL")):
    platform = detect_platform(url)
    if not platform:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Unsupported platform",
                "url": url,
            },
        )

    handler = poster_handlers.get(platform)
    if not handler:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Platform handler is not configured",
                "platform": platform,
            },
        )

    try:
        payload, status_code = await invoke_poster_handler(handler, url)
    except Exception:
        return JSONResponse(
            content={
                "error": "Poster scraper failed",
                "platform": platform,
            },
            status_code=502,
        )

    if isinstance(payload, dict):
        payload = {"platform": platform, **payload}

    return JSONResponse(content=payload, status_code=status_code)


@app.get("/bypass", tags=["Bypass"])
async def bypass(url: str = Query(..., description="Supported file-host URL")):
    try:
        result = direct_link_generator(url)
    except DirectDownloadLinkException as error:
        message = str(error)
        if message.startswith("No Direct link function found"):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Unsupported link",
                    "url": url,
                },
            )
        return JSONResponse(
            content={
                "error": "Direct link resolver failed",
                "message": message,
                "url": url,
            },
            status_code=502,
        )
    except Exception:
        return JSONResponse(
            content={
                "error": "Direct link resolver failed",
                "url": url,
            },
            status_code=502,
        )
    if isinstance(result, tuple):
        payload = {
            "url": url,
            "direct_link": result[0],
        }
        if len(result) > 1:
            payload["headers"] = result[1]
        return JSONResponse(content=payload)
    if isinstance(result, dict):
        return JSONResponse(content={"url": url, **result})
    return JSONResponse(content={"url": url, "direct_link": result})

def anilist_variables(query, media_id):
    if media_id is not None:
        return {"id": media_id}
    value = (query or "").strip()
    if value.isdigit():
        return {"id": int(value)}
    return {"search": value}


def anilist_error(kind, query):
    return HTTPException(
        status_code=404,
        detail={"error": f"{kind} not found", "query": query},
    )


@app.get("/anilist/anime", tags=["AniList"])
async def anilist_anime(
    query: str | None = Query(None, description="Anime name or AniList ID"),
    id: int | None = Query(None, description="AniList anime ID"),
):
    media = await fetch_anime(**anilist_variables(query, id))
    if not media:
        raise anilist_error("Anime", query or str(id))
    return {"service": "anilist", "type": "anime", "data": anime(media)}


@app.get("/anilist/anime/{anime_id}", tags=["AniList"])
async def anilist_anime_by_id(anime_id: int):
    media = await fetch_anime(id=anime_id)
    if not media:
        raise anilist_error("Anime", str(anime_id))
    return {"service": "anilist", "type": "anime", "data": anime(media)}


@app.get("/anilist/character", tags=["AniList"])
async def anilist_character(
    query: str | None = Query(None, description="Character name or AniList ID"),
    id: int | None = Query(None, description="AniList character ID"),
):
    person = await fetch_character(**anilist_variables(query, id))
    if not person:
        raise anilist_error("Character", query or str(id))
    return {"service": "anilist", "type": "character", "data": character(person)}


@app.get("/anilist/manga", tags=["AniList"])
async def anilist_manga(
    query: str | None = Query(None, description="Manga name or AniList ID"),
    id: int | None = Query(None, description="AniList manga ID"),
):
    media = await fetch_manga(**anilist_variables(query, id))
    if not media:
        raise anilist_error("Manga", query or str(id))
    return {"service": "anilist", "type": "manga", "data": manga(media)}


@app.get("/mydramalist", tags=["MyDramaList"])
async def mydramalist_search(query: str = Query(..., description="Drama or movie title")):
    results = await search_dramas(query)
    if not results:
        raise HTTPException(status_code=404, detail={"error": "Drama not found", "query": query})
    return {
        "service": "mydramalist",
        "type": "search",
        "results": [search_item(item) for item in results],
    }


@app.get("/mydramalist/{slug}", tags=["MyDramaList"])
async def mydramalist_detail(slug: str):
    result = await fetch_drama(slug)
    if not result:
        raise HTTPException(status_code=404, detail={"error": "Drama not found", "slug": slug})
    return {"service": "mydramalist", "type": "drama", "data": drama(result)}


@app.get("/imdb", tags=["IMDb"])
async def imdb_search(query: str = Query(..., description="IMDb title or IMDb ID")):
    value = query.strip()
    if value.lower().startswith("tt") or value.isdigit():
        result = await fetch_title(value)
        if not result:
            raise HTTPException(status_code=404, detail={"error": "IMDb title not found", "query": query})
        return {"service": "imdb", "type": "title", "data": title(result)}
    results = await search_titles(value)
    if not results:
        raise HTTPException(status_code=404, detail={"error": "IMDb title not found", "query": query})
    return {"service": "imdb", "type": "search", "results": results}

@app.get("/imdb/{imdb_id}", tags=["IMDb"])
async def imdb_detail(imdb_id: str):
    result = await fetch_title(imdb_id)
    if not result:
        raise HTTPException(status_code=404, detail={"error": "IMDb title not found", "id": imdb_id})
    return {"service": "imdb", "type": "title", "data": title(result)}


@app.get("/tmdb", tags=["TMDB"])
async def tmdb_search(query: str = Query(..., description="Movie or TV series title")):
    result = await resolve(query)
    if not result:
        raise HTTPException(status_code=404, detail={"error": "TMDB title not found", "query": query})
    return {"service": "tmdb", "type": "title", "data": normalize(result)}


@app.get("/bypass/platforms")
def bypass_platforms():
    data = get_supported_bypass_platforms()
    return {
        "count": len(data),
        "platforms": data,
    }

@app.get("/platforms")
def platforms():
    data = get_platforms()
    return {
        "count": len(data),
        "platforms": data,
    }


@app.get("/docs", include_in_schema=False)
async def docs():
    return FileResponse("web/docs.html")

@app.get("/supported")
async def supported_platforms():
    return FileResponse("web/supp.html")

@app.get("/")
async def home():
    return FileResponse("web/home.html")
