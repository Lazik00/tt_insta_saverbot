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


# ===================== PROXY =====================

def load_proxies() -> list[str]:
    proxy_file = Path(__file__).parent / "proxies.txt"
    if not proxy_file.exists():
        return []
    with open(proxy_file, "r") as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]


def get_random_proxy() -> Optional[str]:
    proxies = load_proxies()
    return random.choice(proxies) if proxies else None


# ===================== YDL CONFIG =====================

def _ydl(opts: dict) -> YoutubeDL:
    base = {
        "quiet": False,
        "noprogress": True,
        "nocheckcertificate": True,

        # ⚠️ Instagram uchun eng barqaror qiymatlar
        "retries": 3,
        "fragment_retries": 3,
        "merge_output_format": "mp4",

        # ENG KAM SHUBHALI HEADER
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },

        # Agar cookies bo‘lsa — TAVSIYA QILINADI
        # "cookiefile": "cookies.txt",
    }

    proxy = get_random_proxy()
    if proxy:
        base["proxy"] = proxy

    base.update(opts)
    return YoutubeDL(base)


# ===================== FS HELPERS =====================

def ensure_chat_dir(chat_id: int) -> Path:
    d = DATA_DIR / f"chat_{chat_id}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def cleanup_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


# ===================== MAIN LOGIC =====================

async def download_video_and_audio(
    url: str,
    chat_id: int,
    format_type: str = "both"
) -> Tuple[Optional[Path], Optional[Path], str]:

    workdir = ensure_chat_dir(chat_id) / uuid.uuid4().hex
    workdir.mkdir(parents=True, exist_ok=True)

    video_path = workdir / "video.mp4"
    audio_path = workdir / "audio.mp3"
    gif_path = workdir / "animation.gif"
    image_path = workdir / "image.jpg"

    is_instagram = "instagram.com" in url.lower()
    title = ""

    try:
        # ================= VIDEO =================
        if format_type in ("both", "video"):
            ydl_video_opts = {
                "outtmpl": str(video_path.with_suffix(".%(ext)s")),
                "format": "best[ext=mp4]/best" if is_instagram else "bv*+ba/b",
                "merge_output_format": "mp4",
            }

            with _ydl(ydl_video_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title") or "Media"

            if not video_path.exists():
                produced = list(workdir.glob("video.*"))
                if produced:
                    produced[0].rename(video_path)

            if not video_path.exists():
                raise DownloadError("Video file not found after download")

        # ================= AUDIO =================
        if format_type in ("both", "audio") and video_path.exists():
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-y",
                "-i", str(video_path),
                "-vn",
                "-acodec", "libmp3lame",
                "-b:a", "192k",
                str(audio_path),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.wait()

            if proc.returncode != 0 or not audio_path.exists():
                raise DownloadError("Audio extraction failed")

        return (
            video_path if video_path.exists() else None,
            audio_path if audio_path.exists() else None,
            title,
        )

    except Exception as e:
        cleanup_dir(workdir)
        raise DownloadError(str(e))
