import re
import json
from curl_cffi import requests
import html as html_parser
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def extract_movie_id_from_url(url: str) -> str | None:
    match = re.search(r'-movie-detail-(\d+)', url)
    return match.group(1) if match else None


def extract_next_data(html_text: str) -> dict | None:
    match = re.search(
        r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
        html_text,
        re.DOTALL
    )
    if not match:
        return None

    return json.loads(match.group(1))


def extract_ticketnew_movie(data: dict, movie_id: str) -> dict | None:
    try:
        page_props = data.get("props", {}).get("pageProps", {})
        page_type = page_props.get("type")

        if page_type == "mdp_page":
            server_state = page_props.get("data", {}).get("serverState", {})
            movie_contents = server_state.get("movieContents", {})

            movie = movie_contents.get(movie_id)
            if not movie:
                print("❌ movie_id not found in movieContents")
                return None

            return {
                "title": movie.get("name"),
                "portrait": movie.get("upcomingMoviePosterURL"),
                "landscape": (
                    movie.get("videos", {})
                    .get("videoData", [{}])[0]
                    .get("imageUrl")
                )
            }

        server_state = page_props.get("data", {}).get("serverState", {})
        upcoming_list = (
            server_state.get("upcomingMovies", {})
            .get("upcomingMovieData", [])
        )

        if isinstance(upcoming_list, list) and upcoming_list:
            first = upcoming_list[0].get("ItemDetails", {}).get("MovieData", {})
            return {
                "title": first.get("name"),
                "portrait": first.get("image"),
                "landscape": first.get("video_data", {}).get("thumbnail")
            }

        return None

    except Exception as e:
        print("❌ TicketNew parse error:", e)
        return None

def scrape_ticketnew_movie(url: str):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code != 200:
        return {"error": "Failed to fetch page"}

    html_text = html_parser.unescape(r.text)
    movie_id = extract_movie_id_from_url(url)
    next_data = extract_next_data(html_text)
    if not next_data:
        return {"error": "__NEXT_DATA__ not found"}

    movie = extract_ticketnew_movie(next_data, movie_id)

    if not movie:
        return {"error": "Movie data not found"}

    return movie


@router.get("/ticketnew")
def ticketnew_poster(
    url: str = Query(..., description="TicketNew movie URL")
):
    result = scrape_ticketnew_movie(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
