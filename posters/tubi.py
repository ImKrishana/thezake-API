import json
from curl_cffi import requests
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import uuid

router = APIRouter()

BASE_URL = "https://content-cdn.production-public.tubi.io/api/v3/content"
PROXY = "http://LAZ7qUAFS:1Zry9pHan@156.229.244.111:62584"


def extract_tubi_metadata(data):
    images = data.get("images", {})
    result = {}
    landscape = (
        images.get("landscape_images", [None])[0]
        or images.get("linear_larger_poster", [None])[0]
    )

    portrait = (
        images.get("posterarts", [None])[0]
        or data.get("posterarts", [None])[0]
    )

    logo = None
    if images.get("title_art"):
        logo = images["title_art"][0]

    return {
        "title": f"{data.get('title', '')} - ({data.get('year', '')})",
        "landscape": landscape,
        "portrait": portrait,
        "logo": logo,
    }


def get_tubi_metadata(url, bearer_token):
    content_id = url.rstrip("/").split("/")[-2]
    device_id = str(uuid.uuid4())

    params = {
        "app_id": "tubitv",
        "platform": "web",
        "content_id": content_id,
        "device_id": device_id,
        "include_channels": "true",
        "creator_tensor_app_images[logo]": "w100h100_logo",
        "creator_tensor_app_images[title_art]": "w430h180_title",
        "images[posterarts]": "w600h900_poster",
        "images[hero_422]": "w422h360_hero",
        "images[hero_feature_desktop_tablet]": "w1920h768_hero",
        "images[hero_feature_large_mobile]": "w960h480_hero",
        "images[hero_feature_small_mobile]": "w540h450_hero",
        "images[hero_feature]": "w375h355_hero",
        "images[hero_16x9]": "w1280h720_hero",
        "images[landscape_images]": "w1920h1080_landscape",
        "images[linear_larger_poster]": "w1920h1080_landscape",
        "images[backgrounds]": "w1614h906_background",
        "images[title_art]": "w430h180_title",
    }

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "accept-version": "~5.0.0",
        "authorization": f"Bearer {bearer_token}",
        "origin": "https://tubitv.com",
        "referer": "https://tubitv.com/",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/147.0.0.0 Safari/537.36"
        ),
        "x-capability": '{"content_types":["se"]}',
    }

    resp = requests.get(
                BASE_URL,
                params=params,
                headers=headers,
                impersonate="chrome",
                timeout=30,
            )
    print(f"API Response Status: {resp.status_code}")
    if not resp.ok:
        return None

    return extract_tubi_metadata(resp.json())

@router.get("/tubi")
def tubi_poster(url: str = Query(..., description="Tubi content URL")):
    try:
        bearer_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImQ3ZmEwMmQzLTAwODYtNGYxYS1hM2I0LWM2NGQ3NTkzNTgxNiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJKb2tlbiIsImRldmljZV9pZCI6IjRkYmRiOTMzLTlhZTktNDJmNy1iNGExLWRhMmU3ZTVkNjg4OSIsImV4cCI6MTc3ODc0Mjg3MywiZ2VuZXJhdGlvbiI6IjlkZmUwOTBmLWI5YjctNDQ2My05NWM5LTQwOTUwYWQ5OTg3MiIsImlhdCI6MTc3ODY1NjQ3MywiaXNfZ3Vlc3QiOnRydWUsImlzcyI6IlR1YmkgQWNjb3VudCBTZXJ2aWNlIiwianRpIjoiMzJuZ3Q4cmluaGlrODlqc2NrZnJ0Ymc0IiwibmJmIjoxNzc4NjU2NDczLCJwbGF0Zm9ybSI6IndlYiIsInR1YmlfaWQiOiI2OTJjNDI1MS1iYjZmLTRhY2ItOTcyOS00ODI5OTI0NjFlMGYiLCJ0eXBlIjo1LCJ1dWlkIjoiMzRjOTRkZTItYTc3My00OTIwLWJmZGEtOTQ2YjQ1YjI0MjU0In0.XNPFKmXeCm4m0XFk1gAwqJ4AUl1TbQNkKn_k5p_6-IRUu_0CPVcBoCtnFgxYJX9nUkqbTvUaSN3rVAR6ULFUlyA1U2_xHS4C-QqESUC2FWbkTzF9g20T6fD-8i1k5kOx3nBNyxTUXc5KFUSbIDSryQwdoD9p6Jcd4ZVO1eWyaKrtfosnLYfbsmYUla4jK42XRrUda6DaE4BAacYpfgm7Q99JPFBP-GV-wzhL4-Dbnglj-mFwolOShFByxS2_N4ZXDm7F4cLf7omdPRz1UVkQPscV-M4KBigAlh6Vvq61eDjXPLFGOP5H5dS8niSk1htTfnSpLUJ5D6xYKj5q2XCY8g"
        metadata = get_tubi_metadata(url, bearer_token)
        if metadata:
            return JSONResponse(content=metadata)
        else:
            return JSONResponse(content={"error": "Failed to fetch metadata"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
