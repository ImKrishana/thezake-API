import re
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from curl_cffi import requests

router = APIRouter()

def iq(url: str):
    try:
        html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
        result = {"title": None, "landscape": None, "portrait": None}

        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        if title_match:
            raw_title = title_match.group(1)
            year_match = re.search(r'(.+?\(\d{4}\))', raw_title)
            if year_match:
                result["title"] = year_match.group(1).strip()
            else:
                result["title"] = raw_title.split(" -")[0].strip()

        og_img_match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        if og_img_match:
            base_url = og_img_match.group(1)

            result["landscape"] = re.sub(r'm2_\d+_\d+\.jpg', 'm2_1920_1080.jpg', base_url)
            result["portrait"] = re.sub(r'm2_\d+_\d+\.jpg', 'm2_1500_0.jpg', base_url)

        return result
    except Exception as e:
        return {"error": f"IQYI scraping failed: {str(e)}"}

@router.get("/iqyi")
def iqyi(url: str = Query(..., description="IQYI Series or Movie URL")):
    result = iq(url)
    if "error" in result:
        return JSONResponse(content=result, status_code=400)
    return result
