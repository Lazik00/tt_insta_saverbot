from __future__ import annotations
from urllib.parse import urlparse

SUPPORTED_DOMAINS = {
    # TikTok
    "tiktok.com",
    "www.tiktok.com",
    "vt.tiktok.com",
    "m.tiktok.com",

    # Instagram
    "instagram.com",
    "www.instagram.com",
    "m.instagram.com",

    # YouTube
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "m.youtube.com",

    # Facebook
    "facebook.com",
    "www.facebook.com",
    "m.facebook.com",
    "fb.watch",

    # Twitter/X
    "twitter.com",
    "www.twitter.com",
    "x.com",
    "www.x.com",

    # Twitch
    "twitch.tv",
    "www.twitch.tv",
    "m.twitch.tv",
    "clips.twitch.tv",

    # Pinterest
    "pinterest.com",
    "www.pinterest.com",
    "pin.it",

    # Reddit
    "reddit.com",
    "www.reddit.com",
    "m.reddit.com",

    # Snapchat
    "snap.com",
    "www.snap.com",
    "snapchat.com",

    # Dailymotion
    "dailymotion.com",
    "www.dailymotion.com",
    "dai.ly",

    # Vimeo
    "vimeo.com",
    "www.vimeo.com",

    # Bluesky
    "bsky.app",

    # LinkedIn
    "linkedin.com",
    "www.linkedin.com",

    # Telegram
    "t.me",
    "telegram.me",

    # SoundCloud
    "soundcloud.com",
    "www.soundcloud.com",

    # Spotify
    "spotify.com",
    "www.spotify.com",
    "open.spotify.com",
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