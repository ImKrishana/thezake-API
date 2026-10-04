from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from curl_cffi import requests

router = APIRouter()


class Crunchyroll:
    def __init__(self):
        self.headers = None
        self.session = requests.Session(impersonate="firefox")
        self.bearer = self.get_token()

    def get_token(self):
        self.headers = {"Authorization": "Basic Y3Jfd2ViOg=="}
        r = self.session.post(
            "https://www.crunchyroll.com/auth/v1/token",
            headers=self.headers,
            data={"grant_type": "client_id"},
        )
        return r.json().get("access_token", "")

    def parse_data(self, data):
        return {
            "title": f"{data.get('title')} - {data.get('series_launch_year')}",
            "landscape": data.get("images", {}).get("poster_wide", [[{}]])[0][-1].get("source", ""),
            "portrait": data.get("images", {}).get("poster_tall", [[{}]])[0][-1].get("source", ""),
        }

    def get_poster(self, url: str):
        try:
            cid = url.split("/")[4]
        except Exception:
            return {"error": "Invalid Crunchyroll URL"}

        self.headers = {"Authorization": f"Bearer {self.bearer}"}
        res = self.session.get(
            f"https://www.crunchyroll.com/content/v2/cms/series/{cid}?locale=en-US",
            headers=self.headers,
        )

        if res.status_code != 200:
            return {"error": f"Crunchyroll API failed {res.status_code}", "details": res.text}

        data = res.json()
        if "data" not in data:
            return {"error": "Unexpected API response", "raw": data}

        return self.parse_data(data["data"][0])


@router.get("/crunchyroll")
def crunchyroll_poster(url: str = Query(..., description="Crunchyroll series URL")):
    cr = Crunchyroll()
    result = cr.get_poster(url)
    if "error" in result:
        return JSONResponse(content=result, status_code=400)
    return result
