from __future__ import annotations
from urllib.parse import urlparse

SUPPORTED_DOMAINS = {
    "tiktok.com",
    "www.tiktok.com",
    "vt.tiktok.com",
    "instagram.com",
    "www.instagram.com",
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
}


def is_supported_url(text: str) -> bool:
    try:
        url = text.strip()
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        host = (parsed.netloc or "").lower()
        return any(host.endswith(d) for d in SUPPORTED_DOMAINS)
    except Exception:
        return False