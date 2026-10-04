import re
import json
from curl_cffi import requests
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def _hotstar_transform(url, is_landscape=True):
    if "HOTSTAR_DTH" not in url:
        return url

    if is_landscape:
        return "https://img.airtel.tv/unsafe/fit-in/1920x1080/filters:format(jpg)/" + url
    else:
        return "https://img.airtel.tv/unsafe/fit-in/1500x0/filters:format(jpg)/" + url


def airtel(url: str):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code != 200:
        return {"title": None, "portrait": None, "landscape": None}

    html = r.text

    posters = {
        "title": None,
        "portrait": None,
        "landscape": None
    }

    scripts = re.findall(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        html,
        re.DOTALL
    )

    for script in scripts:
        try:
            data = json.loads(script)
        except Exception:
            continue

        if "name" not in data or "thumbnailUrl" not in data:
            continue

        posters["title"] = data.get("name")

        urls = data.get("thumbnailUrl", [])
        if not isinstance(urls, list):
            urls = [urls]


        for u in urls:
            u_upper = u.upper()

            if not posters["portrait"] and "PORTRAIT" in u_upper:
                posters["portrait"] = _hotstar_transform(u, False)

            if not posters["landscape"] and "LANDSCAPE_169" in u_upper:
                posters["landscape"] = _hotstar_transform(u, True)

        if not posters["landscape"]:
            for u in urls:
                if "LANDSCAPE" in u.upper():
                    posters["landscape"] = _hotstar_transform(u, True)
                    break

        for u in urls:
            if not posters["portrait"] and any(x in u for x in ["1500", "350"]):
                posters["portrait"] = _hotstar_transform(u, False)

            if not posters["landscape"] and any(x in u for x in ["1080", "1280"]):
                posters["landscape"] = _hotstar_transform(u, True)

        break

    return posters

@router.get("/airtel")
def airtel_xtreme_poster(url: str = Query(..., description="Airtel Xtreme content URL")):
    result = airtel(url)
    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
