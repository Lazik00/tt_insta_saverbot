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
        "quiet": True,
        "noprogress": True,
        "nocheckcertificate": True,
        "concurrent_fragment_downloads": 4,
        "retries": 5,
        "fragment_retries": 5,
        "socket_timeout": 30,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        },
        "extractor_args": {
            "youtube": {
                "lang": ["en"],
            }
        },
        "socket_timeout": 30,
        "merge_output_format": "mp4",
    }

    # Add proxy if available
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

    try:
        # Try with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if format_type in ("both", "video"):
                    # Download video
                    ydl_video_opts = {
                        "outtmpl": str(video_path.with_suffix(".%(ext)s")),
                        "format": "bv*+ba/b[ext=mp4]/b",
                        "merge_output_format": "mp4",
                        "quiet": False,
                        "no_warnings": False,
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
                            stderr=asyncio.subprocess.DEVNULL,
                        )
                        await proc.wait()
                        if proc.returncode != 0 or not audio_path.exists():
                            raise DownloadError("ffmpeg failed to extract audio.")

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

                break  # Success, exit retry loop

            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        return (
            video_path if video_path.exists() else None,
            audio_path if audio_path.exists() else None,
            title
        )

    except Exception as e:
        cleanup_dir(workdir)
        raise DownloadError(str(e))