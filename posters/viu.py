from curl_cffi import requests
import json
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def extract_series_info(data):
    import datetime

    try:
        series = data.get("data", {}).get("series", {})

        title = series.get("name", "N/A")

        release_time = series.get("release_time")
        if release_time:
            year = datetime.datetime.fromtimestamp(int(release_time),datetime.UTC).year
        else:
            year = "N/A"

        landscape = series.get("cover_landscape_image_url")
        portrait = series.get("cover_portrait_image_url")

        return {
            "title": f"{title} - ({year})",
            "landscape": landscape,
            "portrait": portrait
        }

    except Exception as e:
        return {"error": str(e)}

def get_viu_details(product_id, proxy=None):
    url = "https://api-gateway-global.viu.com/api/mobile"

    token = "eyJhbGciOiJBMTI4S1ciLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0.sKH-x978I_cF5198O6f3Ak4V_hrR-r54JDugg9LcCAi_7-ElATfkMQ.dR2s0ov4BmQj8b_LvAUS8Q.BZdX1gRyW3H6QTsqxSprnYmnAWBtJ0ZboDk-3e5kkwqft73xbID9M6XENU-adMucvVTFf8Pe6FRzf3RldkVfq7NgAaJlJT75mPbYZhzKxP72fW97Q_Uio769XKQAcKoz_J6WjDa9FT1WX_XqeTfptEKs0NkGAQPsBotAqlKdT8RfjQ0kdzcEFQYPEJK4sy4lsxEUklR6BrdHMXp30zi_HU1_dy-vtqbr0U_aiDEG04A.WBJz3QbDhHaED2dkYuF4SA"

    params = {
        "platform_flag_label": "web",
        "area_id": "2",
        "language_flag_id": "3",
        "platformFlagLabel": "web",
        "areaId": "2",
        "languageFlagId": "3",
        "countryCode": "SG",
        "ut": "0",
        "r": "/vod/detail",
        "product_id": str(product_id),
        "os_flag_id": "1"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://www.viu.com",
        "Referer": "https://www.viu.com/",
        "Accept": "application/json, text/plain, */*",
        "x-forwarded-for": "23.106.248.251",
        "x-viu-ip": "23.106.248.251"
    }

    cookies = {
        "token": token,
        "countryCode": "sg",
        "areaId": "2",
        "platform": "web",
    }

    proxies = None
    if proxy:
        proxies = {"http": proxy, "https": proxy}

    response = requests.get(
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        proxies=proxies,
        impersonate="chrome110",
        timeout=30
    )
    data = response.json()
    return extract_series_info(data)

def extract_porduct_id(url:str) -> str:
    return url.split("/")[7]
@router.get("/viu")
def viu_poster(url: str = Query(..., description="The product ID for the Viu content")):
    try:
        product_id = extract_porduct_id(url)
        details = get_viu_details(product_id)
        return JSONResponse(content=details, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
