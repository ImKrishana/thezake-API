import urllib.request
from urllib.parse import urlparse
import json
import re
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def extract_content_id(url):
    path = urlparse(url).path
    matches = re.findall(r'\b[a-z0-9]{12}\b', path.lower())
    return matches[-1] if matches else None

def fetch_content_data(contentid):
    api = f"https://sainaplaycachedcdn.mobiotics.com/prodv3/subscriber/v1/content/{contentid}?displaylanguage=eng"

    headers = {
        "Accept": "*/*",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXZpY2VpZCI6IjEwMjE1NDUyNDc2MjQwODIiLCJkZXZpY2V0eXBlIjoiUEMiLCJkZXZpY2VvcyI6IldJTkRPV1MiLCJwcm92aWRlcmlkIjoic2FpbmFwbCIsInRpbWVzdGFtcCI6MTc3MTE4MzEyMSwiYXBwdmVyc2lvbiI6IjQ2LjQuMCIsImlwIjoiMy4xNzIuODEuNzYiLCJHZW9Mb2NJcCI6IjEyMy4yNTMuMjM2LjEyMyIsInZpc2l0aW5nY291bnRyeSI6IklOIiwiaXNzdWVyIjoic2FpbmFwbCIsImV4cGlyZXNJbiI6NjA0ODAwLCJwcm92aWRlcm5hbWUiOiJTYWluYSBQbGF5ICIsImlhdCI6MTc3MTE4MzEzMCwiZXhwIjoxNzcxNzg3OTMwLCJpc3MiOiJzYWluYXBsIn0.4HEA54nl6XyoWXLPHbx_f4OZYaaHtp-ZNtdwbVbK83A",
        "Origin": "https://www.sainaplay.com",
        "Referer": "https://www.sainaplay.com/",
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

    return {
        "title": f"{title} - ({year})",
        "landscape": landscape_url,
        "portrait": portrait_url,
    }

@router.get("/sainaplay")
def sainaplay_poster(url: str = Query(..., description="SainaPlay content URL")):
    contentid = extract_content_id(url)
    if not contentid:
        return JSONResponse(content={"error": "Content ID not found in URL"}, status_code=400)

    try:
        data = fetch_content_data(contentid)
        details = extract_details(data)
        return JSONResponse(content=details, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
