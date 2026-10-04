from urllib.parse import urlparse

PLATFORM_DOMAINS = {
    "aaonxt": ("aaonxt.com",),
    "addatimes": ("addatimes.com",),
    "aha": ("aha.video", "ahavideo.com"),
    "airtel": ("airtelxstream.in", "airtel.tv"),
    "amazon": ("primevideo.com", "amazon.com"),
    "apple": ("tv.apple.com",),
    "atrangii": ("atrangii.com",),
    "bms": ("bookmyshow.com",),
    "chaupal": ("chaupal.tv",),
    "crunchyroll": ("crunchyroll.com",),
    "dangal": ("dangalplay.com",),
    "erosnow": ("erosnow.com",),
    "hoichoi": ("hoichoi.tv", "hoichoi.com"),
    "hulu": ("hulu.com",),
    "hungama": ("hungama.com",),
    "iqyi": ("iq.com", "iqiyi.com"),
    "jojo": ("jojoapp.in", "jojo.app"),
    "lionsgate": ("lionsgateplay.com",),
    "mubi": ("mubi.com",),
    "mxplayer": ("mxplayer.in",),
    "nf": ("netflix.com",),
    "playflix": ("playflix.app",),
    "plex": ("plex.tv",),
    "sainaplay": ("sainaplay.com",),
    "shemaroo": ("shemaroome.com", "shemaroo.com"),
    "sonyliv": ("sonyliv.com",),
    "sunnxt": ("sunnxt.com",),
    "tataplay": ("tataplay.com",),
    "ticketnew": ("ticketnew.com",),
    "tubi": ("tubitv.com",),
    "ultra": ("ultratv.com", "ultraplay.com"),
    "ultrajhakaas": ("ultrajhakaas.com",),
    "viki": ("viki.com",),
    "viu": ("viu.com",),
    "viva": ("vivamax.net", "vivamax.com"),
    "wetv": ("wetv.vip",),
    "youku": ("youku.tv", "youku.com"),
    "youtube": ("youtube.com", "youtu.be", "youtube-nocookie.com"),
    "zee5": ("zee5.com",),
    "dailymotion": ("dailymotion.com",)
}


PLATFORM_NAMES = {
    "aaonxt": "AAO NXT",
    "addatimes": "Addatimes",
    "aha": "Aha Video",
    "airtel": "Airtel Xstream",
    "amazon": "Prime Video",
    "apple": "Apple TV+",
    "atrangii": "Atrangii",
    "bms": "BookMyShow",
    "chaupal": "Chaupal",
    "crunchyroll": "Crunchyroll",
    "dangal": "Dangal Play",
    "erosnow": "Eros Now",
    "hoichoi": "Hoichoi",
    "hulu": "Hulu",
    "hungama": "Hungama",
    "iqyi": "iQIYI",
    "jojo": "JOJO",
    "lionsgate": "Lionsgate Play",
    "mubi": "MUBI",
    "mxplayer": "MX Player",
    "nf": "Netflix",
    "playflix": "Playflix",
    "plex": "Plex TV",
    "sainaplay": "Saina Play",
    "shemaroo": "ShemarooMe",
    "sonyliv": "SonyLIV",
    "sunnxt": "Sun NXT",
    "tataplay": "Tata Play",
    "ticketnew": "TicketNew",
    "tubi": "Tubi",
    "ultra": "Ultra",
    "ultrajhakaas": "Ultra Jhakaas",
    "viki": "Viki",
    "viu": "Viu",
    "viva": "Vivamax",
    "wetv": "WeTV",
    "youku": "Youku",
    "youtube": "YouTube",
    "zee5": "ZEE5",
    "dailymotion": "Dailymotion"
}


m6 = "y7kU17MKldfE5PEqYhpunSvKW9vE6rL28Er3teG41yB9jEYM39o060Qmw9zQiv069fFR2w0"
q2 = bytes.fromhex("43726564697473").decode("ascii")


def detect_platform(url):
    try:
        host = urlparse(url).hostname
    except Exception:
        return None

    if not host:
        return None

    host = host.lower()

    for platform, domains in PLATFORM_DOMAINS.items():
        for domain in domains:
            if host == domain or host.endswith("." + domain):
                return platform

    return None


def get_platforms():
    return [
        {
            "id": platform,
            "name": name,
            "domains": PLATFORM_DOMAINS.get(platform, ())
        }
        for platform, name in PLATFORM_NAMES.items()
    ]

__all__ = ["PLATFORM_DOMAINS", "PLATFORM_NAMES", "detect_platform", "get_platforms", "m6", "q2"]
