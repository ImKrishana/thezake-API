import base64
import json
import uuid
import re
import http.client
from binascii import unhexlify
from binascii import hexlify
from Crypto.Cipher import AES
import socketio
import json
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

API_HOST = "api.thesupercms.com"
KEY_B64 = "sBYDzGabIR2aEPagELKBN41kIR7xBm1G5emAODCCLl0="
IV_HEX = "2d8f2f3bfb6a2e6d129f3eaf4ef104d0"

ENCRYPTED_PAYLOAD = "2b5479d1798838006f408d9a9ef9fbaf"

def connect_socket(session_id, device_id):
    sio = socketio.Client()

    sio.connect(
        "https://socket.thesupercms.com",
        headers={
            "Origin": "https://jojoapp.in",
            "User-Agent": "Mozilla/5.0"
        },
        transports=["websocket"],

        auth={
            "devicetypecode": "3",
            "deviceID": device_id,
            "sessionid": session_id,
            "language": 1
        }
    )

    return sio

def encrypt_payload(payload: str):
    key = base64.b64decode("sBYDzGabIR2aEPagELKBN41kIR7xBm1G5emAODCCLl0=")
    iv = unhexlify("2d8f2f3bfb6a2e6d129f3eaf4ef104d0")

    pad = 16 - len(payload) % 16
    payload += chr(pad) * pad

    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(payload.encode())

    return hexlify(encrypted).decode()

def activate_socket(sio):
    payload = {
        "en": "continue-watching"
    }

    encrypted = encrypt_payload(json.dumps(payload))


    sio.emit("req", {
        "data": encrypted
    })

def decrypt_data(encrypted_hex: str) -> dict:
    key = base64.b64decode(KEY_B64)
    iv = unhexlify(IV_HEX)
    ciphertext = unhexlify(encrypted_hex)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext)

    pad_len = decrypted[-1]
    decrypted = decrypted[:-pad_len]

    return json.loads(decrypted.decode("utf-8"))


def get_session():
    device_id = str(uuid.uuid4())

    conn = http.client.HTTPSConnection(API_HOST)

    headers = {
        "appversion":"2.0.0",
        "Accept": "application/json",
        "appversion": "2.0.0",
        "deviceID": device_id,
        "deviceTypeCode": "3",
        "language": "1",
        "Origin": "https://jojoapp.in",
        "Referer": "https://jojoapp.in/",
        "User-Agent": "Mozilla/5.0"
    }

    conn.request("POST", "/auth/guest", "", headers)
    res = conn.getresponse()
    data = res.read().decode()
    conn.close()

    json_data = json.loads(data)
    encrypted = json_data.get("data")

    decrypted = decrypt_data(encrypted)

    session_id = decrypted["data"]["session_id"]

    return session_id, device_id


def fetch_asset(asset_id: int, session_id: str, device_id: str):
    conn = http.client.HTTPSConnection(API_HOST)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "appversion": "2.0.0",
        "deviceID": device_id,
        "deviceTypeCode": "3",
        "language": "1",
        "Origin": "https://jojoapp.in",
        "Referer": "https://jojoapp.in/",
        "User-Agent": "Mozilla/5.0",
        "sessionid": session_id
    }

    body = json.dumps({
        "data": ENCRYPTED_PAYLOAD
    })

    conn.request("POST", f"/asset/{asset_id}", body, headers)
    res = conn.getresponse()
    data = res.read().decode()
    conn.close()

    json_data = json.loads(data)

    encrypted = json_data.get("data")
    if not encrypted:
        return json_data

    decrypted = decrypt_data(encrypted)
    return decrypted

def extract_asset_info(data):
    asset = data.get("data", {})

    title = asset.get("asset_title", "N/A")

    release = asset.get("asset_release_date", "")
    year = release[:4] if release else "N/A"

    landscape_url = None
    for item in asset.get("landscape", []):
        if "content-tile-landscape" in item.get("url", ""):
            landscape_url = item["url"]
            break

    banner_url = None
    for item in asset.get("poster", []):
        if "alpha-banner" in item.get("url", ""):
            banner_url = item["url"]
            break

    portrait_url = None
    for item in asset.get("portrait", []):
        if "content-tile-portrait" in item.get("url", ""):
            portrait_url = item["url"]
            break

    return {
        "title": f"{title} - ({year})",
        "landscape": landscape_url,
        "banner": banner_url,
        "portrait": portrait_url
    }

def extract_asset_id(url: str) -> str:
    """
    Extracts asset ID from URLs like:
    https://jojoapp.in/asset/1318
    https://jojoapp.in/asset/1318?foo=bar
    https://jojoapp.in/asset/1318/#something
    """

    match = re.search(r'/asset/(\d+)', url)
    return match.group(1) if match else None

@router.get("/jojo")
def jojo_poster(url: str = Query(..., description="JoJo app Content URL, e.g. https://jojoapp.in/asset/1318")):
    try:
        asset_id = extract_asset_id(url)
        if not asset_id:
            return JSONResponse(status_code=400, content={"error": "Invalid JoJo URL"})

        session_id, device_id = get_session()
        sio = connect_socket(session_id, device_id)
        activate_socket(sio)

        data = fetch_asset(asset_id, session_id, device_id)

        if "data" not in data:
            return JSONResponse(status_code=404, content={"error": "Asset not found"})

        asset_info = extract_asset_info(data)
        return asset_info

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
