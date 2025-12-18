from __future__ import annotations
import asyncio
import os
import shutil
import uuid
import random
from pathlib import Path
from typing import Tuple, Optional

from yt_dlp import YoutubeDL

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)


class DownloadError(Exception):
    pass


def load_proxies() -> list[str]:
    """Load proxies from proxies.txt file"""
    proxy_file = Path(__file__).parent / "proxies.txt"
    proxies = []
    try:
        if proxy_file.exists():
            with open(proxy_file, 'r') as f:
                proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except Exception as e:
        print(f"Warning: Could not load proxies: {e}")
    return proxies


def get_random_proxy() -> Optional[str]:
    """Get a random proxy from the list"""
    proxies = load_proxies()
    return random.choice(proxies) if proxies else None


def _ydl(opts: dict) -> YoutubeDL:
    base = {
        "quiet": False,  # DEBUG uchun ON
        "noprogress": False,
        "nocheckcertificate": True,
        "concurrent_fragment_downloads": 4,
        "retries": 10,
        "fragment_retries": 10,
        "socket_timeout": 60,
        "extractor_retries": 5,
        # HTTP Headers - Real browser simulatsiyasi
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
            "Referer": "https://www.youtube.com/",
            "Origin": "https://www.youtube.com",
        },
        # YouTube specific extractor args
        "extractor_args": {
            "youtube": {
                "skip": ["hls", "dash", "translated_subs"],
                "lang": ["en"],
                "player_client": ["web"],
            },
            "instagram": {
                "skip_login": False,
            }
        },
        # Timing va rate limiting
        "socket_timeout": 60,
        "merge_output_format": "mp4",
        "sleep_interval": 1,
        "sleep_interval_requests": 2,
        "sleep_interval_subtitles": 1,
        "rate_limit": None,
        # Format selection optimized
        "format_sort": ["res", "fps", "codec:h264", "lang", "ext:mp4"],
        "allow_unplayable_formats": False,
        # Video codec preferences
        "prefer_ffmpeg": True,
        "youtube_include_hls_manifest": False,
        "youtube_include_dash_manifest": False,
        # Client info
        "client_version": "2.20240115.00.00",
        # Fallback options
        "ignore_no_formats_error": True,
        "skip_unavailable_fragments": True,
        # Age gate bypass
        "age_limit": None,
        # Proxy support
        "proxy": None,
    }

    # Proxy qo'llang agar mavjud bo'lsa
    proxy = get_random_proxy()
    if proxy:
        base["proxy"] = proxy

    base.update(opts)
    return YoutubeDL(base)


def ensure_chat_dir(chat_id: int) -> Path:
    d = DATA_DIR / f"chat_{chat_id}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def cleanup_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


async def download_video_and_audio(url: str, chat_id: int, format_type: str = "both") -> Tuple[Optional[Path], Optional[Path], str]:
    """
    Download video and/or audio from various platforms

    Args:
        url: Media URL
        chat_id: Telegram chat ID for organization
        format_type: "both", "video", "audio", "gif", "image"

    Returns: (video_path, audio_path, title)
    Raises: DownloadError
    """
    workdir = ensure_chat_dir(chat_id) / uuid.uuid4().hex
    workdir.mkdir(parents=True, exist_ok=True)

    video_path = workdir / "video.mp4"
    audio_path = workdir / "audio.mp3"
    gif_path = workdir / "animation.gif"
    image_path = workdir / "image.jpg"

    title = ""
    is_instagram = "instagram.com" in url
    is_youtube = "youtube.com" in url or "youtu.be" in url

    try:
        # Try with retry logic
        max_retries = 5 if (is_instagram or is_youtube) else 3

        for attempt in range(max_retries):
            try:
                print(f"[Attempt {attempt + 1}/{max_retries}] Downloading from {url[:50]}...")

                if format_type in ("both", "video"):
                    # Download video
                    ydl_video_opts = {
                        "outtmpl": str(video_path.with_suffix(".%(ext)s")),
                        "format": "bv*+ba/b[ext=mp4]/b",
                        "merge_output_format": "mp4",
                        "quiet": False,
                        "no_warnings": False,
                        # Instagram specific
                        "instagram": {"check_all": True} if is_instagram else {},
                    }

                    with _ydl(ydl_video_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        title = info.get("title") or "Media"

                    # Handle file renaming
                    if not video_path.exists():
                        produced = list(workdir.glob("video.*"))
                        if produced:
                            produced[0].rename(video_path)

                    if not video_path.exists():
                        raise DownloadError("Could not locate downloaded video file.")

                    # Extract audio if requested
                    if format_type in ("both", "audio"):
                        proc = await asyncio.create_subprocess_exec(
                            "ffmpeg", "-y", "-i", str(video_path), "-vn", "-acodec", "libmp3lame", "-b:a", "192k", str(audio_path),
                            stdout=asyncio.subprocess.DEVNULL,
                            stderr=asyncio.subprocess.PIPE,  # Stderr qabul qil
                        )
                        await proc.wait()
                        if proc.returncode != 0 or not audio_path.exists():
                            print(f"⚠️ Audio extraction failed, continuing without audio")
                            # Audio extraction muvaffaqiyatsiz bo'lsa davom et

                elif format_type == "audio":
                    # Download audio only
                    ydl_audio_opts = {
                        "outtmpl": str(audio_path.with_suffix(".%(ext)s")),
                        "format": "ba",
                        "postprocessors": [{
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }],
                    }
                    with _ydl(ydl_audio_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        title = info.get("title") or "Audio"

                elif format_type == "gif":
                    # Download as GIF
                    ydl_gif_opts = {
                        "outtmpl": str(gif_path.with_suffix(".%(ext)s")),
                        "format": "bv*+ba/b",
                    }
                    with _ydl(ydl_gif_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        title = info.get("title") or "Animation"

                elif format_type == "image":
                    # Download thumbnail/image
                    ydl_image_opts = {
                        "outtmpl": str(image_path.with_suffix(".%(ext)s")),
                        "writethumbnail": True,
                        "quiet": True,
                    }
                    with _ydl(ydl_image_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        title = info.get("title") or "Image"

                print(f"✅ Download successful: {title}")
                break  # Success, exit retry loop

            except Exception as e:
                error_msg = str(e).lower()
                if "rate-limit" in error_msg or "sign in to confirm" in error_msg:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = (attempt + 1) * 5  # 5, 10, 15, 20, 25 seconds
                    print(f"⏳ Rate limit/Bot detection. Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                elif attempt == max_retries - 1:
                    raise
                else:
                    wait_time = 2 ** attempt
                    print(f"⚠️ Error: {error_msg[:100]}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)

        return (
            video_path if video_path.exists() else None,
            audio_path if audio_path.exists() else None,
            title
        )

    except Exception as e:
        cleanup_dir(workdir)
        raise DownloadError(str(e))