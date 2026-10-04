import re
import json
from curl_cffi import requests
import html as html_parser
import base64
from datetime import datetime, timezone
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

CDN_BASE = "https://akamaividz2.zee5.com/image/upload/resources"

TITLE_REGEX = r'<h1[^>]*class=["\']title["\'][^>]*>(.*?)</h1>'
MOVIE_TITLE_REGEX = r'<h1[^>]*data-testid=["\']metadata-title["\'][^>]*>(.*?)</h1>'


ZEE5_IMAGE_KEY_MAP = {
    "4k_banner": "landscape",
    "list": "landscape",
    "portrait": "portrait",
    "title_logo": "logo",
    "app_cover": "app_cover",
    "tv_banner": "cover",
}

def generate_token():
    HEADER = {"alg": "HS256", "typ": "JWT"}
    BASE_PAYLOAD = {
        "platform_code": "Web@$!t38712",
        "product_code": "zee5@975",
        "ttl": 86400000
    }
    SIGNATURE = "1jxJ9Qw1PSebtfiuaE3vrSJPyk5aBnADucdU7bPP6gI"

    now = datetime.now(timezone.utc)

    issuedAt = now.isoformat(timespec='milliseconds').replace("+00:00", "Z")
    iat = int(now.timestamp())

    payload = BASE_PAYLOAD.copy()
    payload["issuedAt"] = issuedAt
    payload["iat"] = iat

    header_enc = base64.urlsafe_b64encode(
        json.dumps(HEADER, separators=(",", ":")).encode()
    ).decode().rstrip("=")

    payload_enc = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode().rstrip("=")

    return f"{header_enc}.{payload_enc}.{SIGNATURE}"

def extract_content_id(url: str):
    return url.rstrip("/").split("/")[-1]

def build_zee5_image_urls(image_dict: dict, content_id: str):
    results = {}

    for src_key, dst_key in ZEE5_IMAGE_KEY_MAP.items():
        value = image_dict.get(src_key)
        if value:
            results[dst_key] = f"{CDN_BASE}/{content_id}/{src_key}/{value}"

    return results


def scrape_zee5_meta(url: str):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"}, impersonate="firefox")
    if r.status_code != 200:
        return {"error": "Failed to fetch page"}

    html_text = html_parser.unescape(r.text)
    content_id = extract_content_id(url)

    result = {
        "title": None,
    }

    try:
        next_data = re.search(
            r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
            html_text,
            re.DOTALL
        )

        if next_data:
            json_data = json.loads(next_data.group(1))
            content = json_data["props"]["pageProps"].get("contentLiteData", {})

            if content.get("creative_title"):
                result["title"] = content["creative_title"]
            else:
                movie_title_match = re.search(
                    MOVIE_TITLE_REGEX, html_text, re.IGNORECASE | re.DOTALL
                )
                if movie_title_match:
                    result["title"] = movie_title_match.group(1).strip()

            movie_id = content.get("id")
            image_dict = content.get("image", {})

            if movie_id and image_dict:
                result.update(build_zee5_image_urls(image_dict, movie_id))

                return result

    except Exception as e:
        print("❌ Movie (__NEXT_DATA__) parse error:", e)

    h = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "x-access-token": generate_token()
    }
    api = f"https://gwapi.zee5.com/content/tvshow/{content_id}?translation=en&country=IN"
    res = requests.get(api, headers=h)
    data = res.json()
    if data:
        try:
            title = data.get("title", "")
            release_date = data.get("release_date", "").split("-")[0]
            image = data.get("image", {})
            final_data = build_zee5_image_urls(image, content_id)
            result.update(final_data)
            if title and release_date:
                result["title"] = f"{title} - ({release_date})"
            elif title:
                result["title"] = title
        except Exception as e:
            print("❌ TVShow image parse error:", e)

    return result


@router.get("/zee5")
def zee5_poster(url: str = Query(..., description="ZEE5 content URL")):
    result = scrape_zee5_meta(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
