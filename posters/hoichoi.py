from curl_cffi import requests
import re
from urllib.parse import urlparse, parse_qs
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def get_permalink(url):
    if "permalink=" in url:
        return url.split("permalink=")[-1]
    path = "/" + url.split("/", 3)[-1]
    return path.replace("/", "%2F")

def fetch_hoichoi_data(url):
    client = requests.Session(impersonate="chrome120")
    h = {
        "Accept":"application/json, text/plain, */*",
        "Accept-Encoding":"gzip, deflate, br, zstd",
        "Accept-Language":"en-US,en;q=0.8",
        "Connection":"keep-alive",
        "Origin": "https://hoichoi.tv",
        "Referer": "https://hoichoi.tv/",
        "sec-ch-ua": '"Not=A?Brand";v="99", "Brave";v="151", "Chromium";v="151"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Sec-GPC": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
        "x-bypass-proxy": "true",
        "x-hoichoi-siteid": "hoichoitv"
    }

    permalink = get_permalink(url)

    token_api = "https://prod-api.hoichoi.dev/core/api/v1/users/anonymous-token"

    r1 = client.get(token_api, headers=h)
    anonymous_token = r1.text

    data_api = "https://prod-contents-api.hoichoi.dev/contents/api/v1/contents"
    params = {
        "platform": "WEB",
        "permalink": permalink,
        "language": "english",
        "local": "true",
        "countryCode": "IN"
    }

    h["anonymous-token"] = anonymous_token

    r2 = client.get(data_api, headers=h, params=params)

    return r2.json()

def extract_hoichoi(data):
    item = data

    title = item.get("title")
    year = item.get("releaseYear")
    content_type = item.get("contentType")
    landscape = cover = portrait = logo = None

    if content_type == "series":
        season = item.get("seasons", [])[0]
        images = season.get("images", [])

        title_image = season.get("titleImage")
        if title_image:
            logo = title_image.get("imageUrl")

    else:
        images = item.get("images", [])

        if item.get("titleImage"):
            logo = item["titleImage"].get("imageUrl")

    landscape_list = []

    for img in images:
        reso = img.get("resolution")
        img_url = img.get("imageUrl")

        if reso == "16x9":
            landscape_list.append(img_url)

        elif reso == "3x4" and not portrait:
            portrait = img_url

    if len(landscape_list) >= 1:
        landscape = landscape_list[0]

    if len(landscape_list) >= 2:
        cover = landscape_list[1]

    return {
        "title": f"{title} - ({year})",
        "landscape": landscape,
        "cover": cover,
        "portrait": portrait,
        "logo": logo,
    }


@router.get("/hoichoi")
def hoichoi_endpoint(
    url: str = Query(..., description="Hoichoi movie/series URL")
):
    try:
        data = fetch_hoichoi_data(url)
        result = extract_hoichoi(data)
        return JSONResponse(content=result, status_code=200)

    except Exception as e:
        print("❌ Hoichoi error:", e)
        return JSONResponse(
            content={"error": "Failed to fetch data from Hoichoi"},
            status_code=400
        )
