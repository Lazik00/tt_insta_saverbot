"""
Advanced media saver functionality
"""
from __future__ import annotations
from typing import Optional, Dict, List
import aiohttp
import asyncio
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class MediaInfo:
    """Media haqida ma'lumot"""

    def __init__(self, url: str, title: str, duration: Optional[int] = None,
                 uploader: Optional[str] = None, thumbnail: Optional[str] = None):
        self.url = url
        self.title = title
        self.duration = duration
        self.uploader = uploader
        self.thumbnail = thumbnail

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "title": self.title,
            "duration": self.duration,
            "uploader": self.uploader,
            "thumbnail": self.thumbnail,
        }


class PlaylistDownloader:
    """Playlist yuklab olish"""

    def __init__(self):
        self.queue: List[str] = []

    async def add_to_queue(self, url: str) -> None:
        """URL ni chuvalga qo'shish"""
        self.queue.append(url)
        logger.info(f"✅ {url} chuvalga qo'shildi. Jami: {len(self.queue)}")

    async def process_queue(self, chat_id: int) -> None:
        """Chuvalni qayta ishlash"""
        while self.queue:
            url = self.queue.pop(0)
            logger.info(f"🔄 {url} qayta ishlanmoqda...")
            # Download logic here
            await asyncio.sleep(1)


class StreamRecorder:
    """Stream yozib olish (Twitch, YouTube Live va boshqa)"""

    def __init__(self, url: str, output_path: Path):
        self.url = url
        self.output_path = output_path
        self.recording = False

    async def start_recording(self) -> None:
        """Yozish boshlash"""
        self.recording = True
        logger.info(f"🔴 Yozish boshlandi: {self.url}")

    async def stop_recording(self) -> None:
        """Yozishni to'xtatish"""
        self.recording = False
        logger.info(f"⏹️ Yozish to'xtatildi")


class MediaConverter:
    """Media formatlarini konversiya qilish"""

    @staticmethod
    async def convert_video(input_path: Path, output_path: Path,
                           codec: str = "libx264", quality: str = "medium") -> bool:
        """Video konversiyasi"""
        logger.info(f"🎬 Video konversiyasi: {input_path} -> {output_path}")
        # Implement conversion
        return True

    @staticmethod
    async def convert_audio(input_path: Path, output_path: Path,
                           bitrate: str = "192k") -> bool:
        """Audio konversiyasi"""
        logger.info(f"🎧 Audio konversiyasi: {input_path} -> {output_path}")
        # Implement conversion
        return True

    @staticmethod
    async def extract_subtitle(video_path: Path, output_path: Path,
                              language: str = "en") -> Optional[Path]:
        """Subtitrlarni ajratish"""
        logger.info(f"📝 Subtitrlar ajratilmoqda...")
        return output_path if output_path.exists() else None


class MetadataExtractor:
    """Metadata ajratish"""

    @staticmethod
    def extract_from_file(file_path: Path) -> Dict:
        """Fayldan metadata ajratish"""
        return {
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "created_at": file_path.stat().st_ctime,
        }

    @staticmethod
    async def fetch_remote_metadata(url: str) -> Optional[MediaInfo]:
        """Remote metadata olish"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, allow_redirects=True, timeout=10) as resp:
                    if resp.status == 200:
                        return MediaInfo(url, "Title", duration=None)
        except Exception as e:
            logger.error(f"Metadata olishda xatolik: {e}")
        return None


async def batch_download(urls: List[str], chat_id: int) -> Dict[str, List[str]]:
    """Batch yuklab olish"""
    from app.utils import download_video_and_audio

    results = {
        "success": [],
        "failed": [],
    }

    for url in urls:
        try:
            video, audio, title = await download_video_and_audio(url, chat_id)
            results["success"].append(url)
            logger.info(f"✅ Muvaffaqiyatli: {url}")
        except Exception as e:
            results["failed"].append(url)
            logger.error(f"❌ Xatolik: {url} - {e}")

    return results

