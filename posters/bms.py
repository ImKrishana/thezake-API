import re
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from curl_cffi import requests

router = APIRouter()

def bms(url: str):
    try:
        session = requests.Session(impersonate="firefox")
        resp = session.get(url)
        html = resp.text

        title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        movie_title = None
        if title_match:
            raw_title = title_match.group(1).strip()
            clean_match = re.search(r"^(.*?\(\d{4}\))", raw_title)
            if clean_match:
                movie_title = clean_match.group(1)

        pattern = r"https://assets-in\.bmscdn\.com/discovery-catalog/events/[^\s\"']+"
        matches = list(set(re.findall(pattern, html)))
        images = {}
        for u in matches:
            if "landscape" in u:
                images["landscape"] = u
            elif "portrait" in u:
                images["portrait"] = re.sub(r"tr:[^/]+/", "", u)

        return {
            "title": movie_title,
            "landscape": images.get("landscape"),
            "portrait": images.get("portrait")
        }

    except Exception as e:
        return {"error": f"BookMyShow scraping failed: {str(e)}"}

@router.get("/bms")
def bookmyshow_poster(url: str = Query(..., description="BookMyShow movie URL")):
    result = bms(url)
    if "error" in result:
        return JSONResponse(content=result, status_code=400)
    return result
