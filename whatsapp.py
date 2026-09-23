import hashlib
import hmac
import logging
import os

import httpx

log = logging.getLogger("whatsapp")

TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_ID = os.getenv("PHONE_NUMBER_ID", "")
APP_SECRET = os.getenv("APP_SECRET", "")
API = f"https://graph.facebook.com/{os.getenv('GRAPH_VERSION', 'v21.0')}/{PHONE_ID}/messages"


VER = os.getenv("GRAPH_VERSION", "v21.0")


def download_media(media_id: str):
    h = {"Authorization": f"Bearer {TOKEN}"}
    meta = httpx.get(f"https://graph.facebook.com/{VER}/{media_id}", headers=h, timeout=15)
    meta.raise_for_status()
    j = meta.json()
    f = httpx.get(j["url"], headers=h, timeout=30)
    f.raise_for_status()
    return f.content, j.get("mime_type", "audio/ogg")


def send_text(to: str, body: str) -> None:
    r = httpx.post(
        API,
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": body},
        },
        timeout=15,
    )
    if r.status_code >= 400:
        log.error("send failed %s: %s", r.status_code, r.text)


def valid_signature(raw: bytes, header: str | None) -> bool:
    if not APP_SECRET or not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(APP_SECRET.encode(), raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header[7:])
