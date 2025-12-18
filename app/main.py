from __future__ import annotations
import asyncio
import logging
import os
from contextlib import suppress
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hlink
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties

from app.utils import download_video_and_audio, cleanup_dir, ensure_chat_dir, DownloadError
from app.validators import is_supported_url
from app.database import init_db, add_user, add_download, get_user_download_count, is_premium
from app.admin import admin_router

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", "0")) or 0

if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN is not set. Put it into .env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("bot")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)


async def on_startup() -> None:
    logger.info("Bot started")
    await init_db()
    logger.info("Database initialized")


async def on_shutdown() -> None:
    logger.info("Bot stopped")


async def handle_start(msg: Message):
    text = (
        "👋 <b>Salom!</b>\n\n"
        "Menga quyidagi manbalardan havolalar yuboring:\n"
        "• TikTok\n"
        "• Instagram Reels\n"
        "• YouTube Videolar\n\n"
        "Men esa sizga <b>video MP4</b> va alohida <b>audio MP3</b> qilib yuboraman.\n\n"
        "📹 <b>Misollar:</b>\n"
        f"• {hlink('TikTok', 'https://www.tiktok.com')}\n"
        f"• {hlink('Instagram Reels', 'https://www.instagram.com')}\n"
        f"• {hlink('YouTube', 'https://www.youtube.com')}\n\n"
        "⚖️ Faqat o'zingizga tegishli yoki ruxsat etilgan kontentni yuklab oling."
    )

    await add_user(msg.from_user.id, msg.from_user.username)
    await msg.answer(text, disable_web_page_preview=True)


async def handle_link(msg: Message):
    url = (msg.text or "").strip()
    if not is_supported_url(url):
        await msg.reply("❌ Link noto'g'ri yoki qo'llab-quvvatlanmaydi. TikTok/Instagram/YouTube havolasini yuboring.")
        return

    user_id = msg.from_user.id
    download_count = await get_user_download_count(user_id)

    # Premium users get faster service (no ads/delays)
    user_premium = await is_premium(user_id)

    await msg.answer("⏳ Yuklab olish va audio ajratish boshlandi… Bir oz kuting.")

    chat_dir = ensure_chat_dir(msg.chat.id)
    video_path: Path | None = None
    audio_path: Path | None = None

    try:
        video_path, audio_path, title = await download_video_and_audio(url, msg.chat.id)

        # Log download
        await add_download(user_id, url)

        # Size guard if configured
        if MAX_UPLOAD_BYTES and video_path.stat().st_size > MAX_UPLOAD_BYTES:
            await msg.answer("⚠️ Video hajmi juda katta. Konfiguratsiyada MAX_UPLOAD_BYTES ni oshiring yoki linkni boshqa formatda yuboring.")
        else:
            video_file = FSInputFile(path=video_path)
            await msg.answer_video(video=video_file, caption=f"🎬 <b>{title}</b>")

        if MAX_UPLOAD_BYTES and audio_path.stat().st_size > MAX_UPLOAD_BYTES:
            await msg.answer("⚠️ Audio hajmi juda katta. MP3 sifatini kamaytirish kerak bo'lishi mumkin.")
        else:
            audio_file = FSInputFile(path=audio_path)
            await msg.answer_audio(audio=audio_file, caption=f"🎧 {title} — Audio (MP3)")

    except DownloadError as e:
        logger.exception("Download failed: %s", e)
        await msg.answer("❌ Yuklab olish muvaffaqiyatsiz. Linkni tekshirib, qayta urinib ko'ring.")
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        await msg.answer("💥 Kutilmagan xatolik yuz berdi. Keyinroq urinib ko'ring.")
    finally:
        # Clean per-task subdir but keep chat root dir
        with suppress(Exception):
            if video_path is not None:
                cleanup_dir(video_path.parent)
            elif audio_path is not None:
                cleanup_dir(audio_path.parent)


async def main() -> None:
    dp = Dispatcher()
    dp.include_router(admin_router)
    dp.message.register(handle_start, CommandStart())
    dp.message.register(handle_link, F.text)

    await on_startup()
    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    finally:
        await bot.session.close()
        await on_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
