import os

import httpx


def transcribe(audio: bytes, mime: str) -> str | None:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    r = httpx.post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {key}"},
        files={"file": ("voice.ogg", audio, mime or "audio/ogg")},
        data={"model": os.getenv("STT_MODEL", "whisper-1"), "language": os.getenv("STT_LANG", "ar")},
        timeout=60,
    )
    r.raise_for_status()
    return (r.json().get("text") or "").strip() or None
