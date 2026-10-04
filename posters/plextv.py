from curl_cffi import requests
import re
import json
import html as html_lib
from urllib.parse import unquote
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def clean_title(text: str) -> str | None:
    text = text.strip()

    pattern0 = r"^(.*?)\s*(?:•|-)\s*(Season\s*\d+).*?Release Date.*"
    match0 = re.search(pattern0, text, re.IGNORECASE)

    if match0:
        title = match0.group(1).strip()
        season = match0.group(2).strip()
        return f"{title} {season}"

    pattern1 = r"Watch\s+(.*?)\s+(?:TV Show|Full Movie|Movie)"
    match1 = re.search(pattern1, text, re.IGNORECASE)

    if match1:
        return match1.group(1).strip()

    pattern2 = r"^(.*?)\s*\(\d{4}\)"
    match2 = re.search(pattern2, text)

    if match2:
        title = match2.group(1).strip()
        year = re.search(r"\(\d{4}\)", text)
        return f"{title} {year.group(0)}" if year else title

    return text.strip()

def extract_balanced_json(text, start_pattern):
    """
    Extract balanced JSON object starting from a pattern like '"seo":{'
    """
    match = re.search(start_pattern, text)
    if not match:
        return None

    start = match.end() - 1
    brace_count = 0

    for i in range(start, len(text)):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1

            if brace_count == 0:
                return text[start:i+1]

    return None


def plex(url):
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.7",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Referer": url,
        "rsc": "1"
    }

    cookies = {
        "NEXT_LOCALE": "no"
    }

    response = requests.get(url, headers=headers, cookies=cookies)
    html = response.text
    result = {}

    inner_html_match = re.search(r'"__html"\s*:\s*"({.*?})"\s*}', html)
    if inner_html_match:
        try:
            raw_json_str = inner_html_match.group(1).replace('\\"', '"').replace('\\\\', '\\')
            script_data = json.loads(raw_json_str)

            graph = script_data.get("@graph", [])
            for item in graph:
                if item.get("@type") in ["TVSeries", "Movie", "Show"]:
                    if "name" in item:
                        result["title"] = item["name"]
                    if "image" in item:
                        result["portrait"] = item["image"].replace("&amp;", "&")
        except Exception:
            pass

    if "title" not in result or "year" not in result:
        metadata_match = re.search(r'"metadataItem"\s*:\s*({.*?})', html)
        if metadata_match:
            try:
                metadata = json.loads(metadata_match.group(1))
                if "title" in metadata and not result.get("title"):
                    result["title"] = metadata["title"]

                if "releaseDate" in metadata:
                    year_match = re.search(r'\d{4}', metadata["releaseDate"])
                    if year_match:
                        year = year_match.group(0)
            except Exception:
                if not result.get("title"):
                    t_match = re.search(r'"title"\s*:\s*"([^"]+)"', html)
                    if t_match: result["title"] = t_match.group(1)

                y_match = re.search(r'"releaseDate"\s*:\s*"(\d{4})', html)
                if y_match: year = y_match.group(1)

    og_image_match = re.search(r'{"property"\s*:\s*"og:image"\s*,\s*"content"\s*:\s*"([^"]+)"}', html)
    if og_image_match:
        result["landscape"] = og_image_match.group(1).replace("&amp;", "&")

    title = result.get("title", "Unknown Title")

    if year:
        result["title"] = f"{title} - ({year})"
    else:
        result["title"] = title

    return result

@router.get("/plex")
def plex_poster(url: str = Query(..., description="Plex content URL")):
    result = plex(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
