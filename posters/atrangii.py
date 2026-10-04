from curl_cffi import requests
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def atrangii(url):
    slug = url.split("/")[-1]
    api = (
        "https://gway.atrangii.in/r/api/ullu2/media/"
        "getMediaByTitleYearSlugAndFamilySafe/cdiOpn"
    )

    headers = {
        "User-Agent": "okhttp/4.9.3",
        "Accept": "application/json",
        "Origin": "https://atrangii.in",
        "Referer": "https://atrangii.in/",
        "x-appname": "Atrangii-Android",
    }

    for family_safe in ("no", "yes"):
        resp = requests.get(
            api,
            headers=headers,
            params={
                "familySafe": family_safe,
                "titleYearSlug": slug
            },
            timeout=20
        )

        try:
            data = resp.json()
        except Exception:
            continue

        if data.get("code") == 116:
            continue

        try:
            meta = data["mainContent"]["contentMetaData"]

            title = meta["title"]
            year = meta["titleYearSlug"].split("-")[-1]
            posters = meta.get("posters", [])

            landscape = None
            portrait = None

            if len(posters) > 0:
                landscape = (
                    "https://images.weserv.nl/?url=media-files.atrangii.in"
                    + posters[0]["fileId"]
                )

            if len(posters) > 1:
                portrait = (
                    "https://images.weserv.nl/?url=media-files.atrangii.in"
                    + posters[1]["fileId"]
                )

            return {
                "title": f"{title} - ({year})",
                "landscape": landscape,
                "portrait": portrait
            }

        except Exception:
            return "failed to fetch"

    return "failed to fetch"

@router.get("/atrangii")
def atrangii_poster(url:str = Query(..., description="Atrangii Content Url")):
    result = atrangii(url)
    if "error" in result:
        return JSONResponse(content=result, status_code=400)
    return JSONResponse(content=result, status_code=200)
