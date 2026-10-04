from curl_cffi import requests
import urllib.parse
import json
import re
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def extract_object(text, key):
    import re, json

    pattern = rf'"{key}"\s*:\s*\{{'
    match = re.search(pattern, text)

    if not match:
        return None

    start = match.end() - 1
    stack = 0

    for i in range(start, len(text)):
        if text[i] == "{":
            stack += 1
        elif text[i] == "}":
            stack -= 1
            if stack == 0:
                try:
                    return json.loads(text[start:i+1])
                except:
                    return None
    return None


def extract_addatimes(text):
    data = extract_object(text, "movie")

    if data:
        return data

    return extract_object(text, "series")


def clean_rsc_text(text):
    lines = text.splitlines()
    cleaned = []

    for line in lines:
        if ":" in line:
            line = line.split(":", 1)[1]
        cleaned.append(line)

    return "".join(cleaned)

def get_year(data):
    year = (
        data.get("publish_date") or
        data.get("year_of_production")
    )

    if not year and "top_video" in data:
        top = data["top_video"]
        year = (
            top.get("publish_date") or
            top.get("year_of_production")
        )

    return year[:4] if year else ""


def fetch_addatimes(url):
    path = url.split("addatimes.com/")[-1]
    slug = path.split("/")[-1]
    content_type = "movie" if "movie" in path else "series"

    tree = [
        "",
        {
            "children": [
                content_type,
                {
                    "children": [
                        ["slug", slug, "d"],
                        {
                            "children": ["__PAGE__", {}, None, None]
                        },
                        None,
                        None
                    ]
                },
                None,
                "refetch"
            ]
        },
        None,
        None
    ]

    encoded_tree = urllib.parse.quote(json.dumps(tree, separators=(',', ':')))

    headers = {
        "Accept": "*/*",
        "RSC": "1",
        "Next-Router-State-Tree": encoded_tree,
        "Referer": "https://www.addatimes.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(
        url + "?_rsc=1",
        headers=headers,
        impersonate="chrome124"
    )

    text = response.content.decode("utf-8", errors="ignore")
    data = extract_addatimes(text)

    if not data:
        print("❌ Failed to extract data")
        return None

    result = {
        "title": f"{data.get('title') or data.get('name')} - ({get_year(data)})",
        "landscape": data.get("horizontal_image"),
        "portrait": data.get("vertical_image"),
        "cover": data.get("horizontal_image_no_logo"),
        "logo": data.get("logo"),
        "banner": data.get("tv_background")
    }

    return result

@router.get("/addatimes")
def addatimes_poster(url: str = Query(..., description="Addatimes content URL")):
    result = fetch_addatimes(url)

    if not result:
        return JSONResponse(content={"error": "Failed to fetch data from Addatimes"}, status_code=400)

    return JSONResponse(content=result, status_code=200)
