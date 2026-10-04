from curl_cffi import requests
import re
import uuid
import time
from urllib.parse import urlparse
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

class SonyLivExtractor:
    def __init__(self, page_url):
        self.page_url = page_url
        self.end_code = self._extract_end_code(page_url)

        self.device_id = f"{uuid.uuid4()}-{int(time.time()*1000)}"
        self.session_id = f"{uuid.uuid4()}-{int(time.time()*1000)}"

        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json",
            "Origin": "https://www.sonyliv.com",
            "Referer": "https://www.sonyliv.com/",
            "app_version": "3.6.56",

            "device_id": self.device_id,
            "session_id": self.session_id,
            "X-AVS-Platform": "WEB",
            "X-AVS-Country": "IN",
            "x-via-device": "true",
        }

    def _extract_end_code(self, url):
        path = urlparse(url).path

        m = re.search(r'-(\d+)$', path)
        if not m:
            raise ValueError("Invalid SonyLIV URL")

        return m.group(1)

    def _find_first(self, obj, keys):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in keys and isinstance(v, str) and v.startswith("http"):
                    return v
                found = self._find_first(v, keys)
                if found:
                    return found
        elif isinstance(obj, list):
            for item in obj:
                found = self._find_first(item, keys)
                if found:
                    return found
        return None

    def prime_watchhistory(self):
        url = (
            "https://apiv2.sonyliv.com/AGL/2.6/A/ENG/WEB/IN/ALL/"
            f"WATCHHISTORY/SHOW/{self.end_code}"
        )

        requests.get(
            url,
            headers=self.base_headers,
            params={"kids_safe": "false"},
            timeout=20
        )

    def get_content_id(self):
        self.prime_watchhistory()

        url = (
            "https://apiv2.sonyliv.com/AGL/4.8/A/ENG/WEB/IN/GJ/"
            f"USER/RECOMMENDATION/DETAIL/{self.end_code}"
        )

        params = {
            "kids_safe": "false",
            "from": "0",
            "to": "9",
            "segment_id": "AB_DetailPage_Disable"
        }

        r = requests.get(
            url,
            headers={**self.base_headers, "liv_id": self.device_id},
            params=params,
            timeout=20
        ).json()

        containers = r.get("resultObj", {}).get("containers", [])
        for c in containers:
            suggestions = c.get("suggestions")
            if not suggestions:
                continue

            cta = suggestions.get("button_cta", "")
            if cta.startswith("sony://asset/"):
                return cta.split("/")[-1]

        return None

    def extract_title(self, detail_json):
        containers = detail_json.get("resultObj", {}).get("containers", [])

        for c in containers:
            metadata = c.get("metadata", {})
            title = metadata.get("title")
            if title:
                return title

            assets = c.get("assets", {})
            for item in assets.get("containers", []):
                meta = item.get("metadata", {})
                title = meta.get("title")
                if title:
                    return title

        return None

    def get_images(self):
        content_id = self.get_content_id()
        if not content_id:
            raise Exception("Content ID not found")

        url = (
            "https://apiv3.sonyliv.com/AGL/4.8/A/ENG/WEB/IN/MH/"
            f"DETAIL-V2/{content_id}"
        )

        params = {
            "kids_safe": "false",
            "from": "0",
            "to": "9"
        }

        headers = {
            "User-Agent": self.base_headers["User-Agent"],
            "Origin": self.base_headers["Origin"],
            "Referer": self.base_headers["Referer"],
            "app_version": self.base_headers["app_version"],
            "Accept": "application/json"
        }

        data = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        ).json()

        return {
            "title": self.extract_title(data),
            "landscape": self._find_first(data, {"thumbnail"}),
            "portrait": self._find_first(data, {"portrait_thumb", "portraitThumb"}),
            "cover": self._find_first(data, {"masthead_web_v1", "masthead"})
        }

@router.get("/sonyliv")
def sonyliv_poster(
    url: str = Query(..., description="Sonyliv content URL")
):
    sl = SonyLivExtractor(url)
    result = sl.get_images()

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
