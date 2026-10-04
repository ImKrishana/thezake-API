from curl_cffi import requests
import json
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def ultra(url: str):
    title_id = url.strip("/").split("/")[-1]
    try:
        api_url = f"https://ultraplay.gror5288.workers.dev/?id={title_id}"
        res = requests.get(api_url)
        data = res.json()

        title = data.get("title", "Unknown")
        publish = data.get("publishYear", "Unknown")

        landscape = data.get("portraitImage", "")
        portrait = data.get("thumbnailImage", "")

        return {
            "title": title,
            "publish": publish,
            "landscape": landscape,
            "portrait": portrait
        }
    except json.JSONDecodeError:
        return {"error": "JSON decode error"}

@router.get("/ultra")
def ultraplay_poster(url: str = Query(..., description="Ultra content URL")):
    result = ultra(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
