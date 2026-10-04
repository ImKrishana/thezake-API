import urllib.request
import json
import re
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def extract_content_id(url):
    matches = re.findall(r'\b[a-z0-9]{12}\b', url.lower())
    return matches[-1] if matches else None

def fetch_content_data(contentid):
    api = f"https://ultracachedcdn.mobiotics.com/prodv3/subscriber/v1/content/{contentid}?displaylanguage=eng"

    headers = {
        "Accept": "*/*",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXZpY2VpZCI6IjMwMzEwNTIzMDg0NzE4NjkiLCJkZXZpY2V0eXBlIjoiUEMiLCJkZXZpY2VvcyI6IldJTkRPV1MiLCJwcm92aWRlcmlkIjoidWx0cmFqaHMiLCJ0aW1lc3RhbXAiOjE3NzEwOTkyNjYsImFwcHZlcnNpb24iOiI0Ni40LjAiLCJpcCI6IjMuMTcyLjgxLjExMSIsIkdlb0xvY0lwIjoiMTIzLjI1My4yMzYuMTIzIiwidmlzaXRpbmdjb3VudHJ5IjoiSU4iLCJpc3N1ZXIiOiJ1bHRyYWpocyIsImV4cGlyZXNJbiI6NzIwMCwicHJvdmlkZXJuYW1lIjoiVWx0cmEgSmhha2FhcyIsImlhdCI6MTc3MTA5OTI3MiwiZXhwIjoxNzcxMTA2NDcyLCJpc3MiOiJ1bHRyYWpocyJ9.D7l9Ixyn7OxOTULBwH4fXXRS_NamVE0BNKyFwPOCkzI",
        "Origin": "https://www.ultrajhakaas.com",
        "Referer": "https://www.ultrajhakaas.com/",
        "User-Agent": "Mozilla/5.0"
    }

    req = urllib.request.Request(api, headers=headers)

    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())

    return data


def extract_details(data):
    title = data.get("title", "N/A")
    publish_time = data.get("publishtime", "")

    year = publish_time.split("-")[0] if publish_time else "N/A"

    landscape_url = None
    portrait_url = None
    banner_url = None

    posters = data.get("poster", [])

    for poster in posters:
        postertype = poster.get("postertype", "").upper()

        for file in poster.get("filelist", []):
            if file.get("quality") == "HD":
                url = file.get("filename")

                if postertype == "LANDSCAPE":
                    landscape_url = url
                elif postertype == "PORTRAIT":
                    portrait_url = url
                elif postertype == "WIDE":
                    banner_url = url

    return {
        "title": f"{title} - ({year})",
        "landscape": landscape_url,
        "portrait": portrait_url,
        "banner": banner_url
    }

@router.get("/ultrajhakaas")
def ultrajhakaas_poster(url: str = Query(..., description="Ultra Jhakaas content URL")):
    contentid = extract_content_id(url)
    if not contentid:
        return JSONResponse(content={"error": "Content ID not found in URL"}, status_code=400)

    try:
        data = fetch_content_data(contentid)
        details = extract_details(data)
        return JSONResponse(content=details, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
