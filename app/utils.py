from __future__ import annotations
import asyncio
import os
import shutil
import uuid
from pathlib import Path
from typing import Tuple

from yt_dlp import YoutubeDL

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)


class DownloadError(Exception):
    pass


def _ydl(opts: dict) -> YoutubeDL:
    base = {
        "quiet": True,
        "noprogress": True,
        "nocheckcertificate": True,
        "concurrent_fragment_downloads": 4,
        # speed/robustness tweaks
        "retries": 3,
        "fragment_retries": 3,
        "http_headers": {
            # mimic a browser a bit
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    }
    base.update(opts)
    return YoutubeDL(base)


def ensure_chat_dir(chat_id: int) -> Path:
    d = DATA_DIR / f"chat_{chat_id}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def cleanup_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


async def download_video_and_audio(url: str, chat_id: int) -> Tuple[Path, Path, str]:
    """
    Returns: (video_path, audio_path, title)
    Raises: DownloadError
    """
    workdir = ensure_chat_dir(chat_id) / uuid.uuid4().hex
    workdir.mkdir(parents=True, exist_ok=True)

    video_path = workdir / "video.mp4"
    audio_path = workdir / "audio.mp3"

    # 1) Fetch best MP4 video (merge if needed)
    ydl_video_opts = {
        "outtmpl": str(video_path.with_suffix(".%(ext)s")),
        # Prefer mp4 output; fallback to best
        "format": "bv*+ba/b[ext=mp4]/b",
        "merge_output_format": "mp4",
    }

    title = ""
    try:
        with _ydl(ydl_video_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title") or "Video"

        # If yt-dlp chose non-mp4, move/rename to video.mp4 if possible
        # (yt-dlp respects merge_output_format=mp4)
        if not video_path.exists():
            # Find produced file (wildcard)
            produced = list(workdir.glob("video.*"))
            if produced:
                produced[0].rename(video_path)

        if not video_path.exists():
            raise DownloadError("Could not locate downloaded video file.")

        # 2) Extract audio from the downloaded video using ffmpeg
        # Avoid re-downloading from source
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-i", str(video_path), "-vn", "-acodec", "libmp3lame", "-b:a", "192k", str(audio_path),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        if proc.returncode != 0 or not audio_path.exists():
            raise DownloadError("ffmpeg failed to extract audio.")

        return video_path, audio_path, title

    except Exception as e:
        # Clean the workspace but preserve parent chat dir
        cleanup_dir(workdir)
        raise DownloadError(str(e))