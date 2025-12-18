from __future__ import annotations
import asyncio
import logging
import os
from contextlib import suppress
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hlink
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from app.admin import admin_router
from app.database import db
from app.user_panel import logger_router
from app.utils import download_video_and_audio, cleanup_dir, ensure_chat_dir, DownloadError
from app.validators import is_supported_url
from app.config import BOT_TOKEN, MAX_UPLOAD_BYTES

load_dotenv()

if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
    raise SystemExit(
        "❌ BOT_TOKEN .env fayliga qo'shilishi kerak!\n"
        "📝 .env fayliga BotFather dan olgan bot tokenini kiriting\n"
        "🔗 https://t.me/BotFather"
    )

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("bot")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)


class DownloadState(StatesGroup):
    waiting_for_url = State()
    waiting_for_format = State()


async def on_startup() -> None:
    logger.info("Bot started")
    db.init_db()  # Database tables yaratish
    logger.info("✅ Database initialized")

    # Admin IDlar
    ADMIN_IDS = [5773429637]  # Admin user IDs

    # Adminlarni database ga qo'shish
    for admin_id in ADMIN_IDS:
        user = db.get_user(admin_id)
        if not user:
            db.add_user(admin_id, username="admin", first_name="Admin", is_admin=True)
            logger.info(f"✅ Admin qo'shildi: {admin_id}")
        elif not user.get('is_admin'):
            db.make_admin(admin_id)
            logger.info(f"✅ {admin_id} admin qilindi")


async def on_shutdown() -> None:
    logger.info("Bot stopped")


async def handle_start(msg: Message):
    text = (
        "🎬 <b>Ko'p Platformali Media Yuklovchi Bot</b>\n\n"
        "Salom! Menga video/audio havolasini yuboring.\n\n"
        "<b>Qo'llab-quvvatlanuvchi platformalar:</b>\n"
        "✅ TikTok\n"
        "✅ Instagram (Reels)\n"
        "✅ YouTube\n"
        "✅ Facebook\n"
        "✅ Twitter/X\n"
        "✅ Twitch\n"
        "✅ Pinterest\n"
        "✅ Reddit\n"
        "✅ Snapchat\n"
        "✅ Dailymotion\n"
        "✅ Vimeo\n"
        "✅ Bluesky\n"
        "✅ LinkedIn\n"
        "✅ SoundCloud\n"
        "✅ Va boshqa ko'plab platformalar...\n\n"
        "<b>Foydalanish:</b>\n"
        "1️⃣ Mediya havolasini yuboring\n"
        "2️⃣ Format turini tanlang (Video, Audio, GIF yoki Image)\n"
        "3️⃣ Bot yuklaydi va sizga yuboradi\n\n"
        "/help - Batafsil ma'lumot\n"
        "/formats - Qo'llab-quvvatlanuvchi formatlar\n\n"
        "⚖️ Faqat o'zingizga tegishli yoki ruxsat etilgan kontentni yuklab oling."
    )
    await msg.answer(text, disable_web_page_preview=True)


async def handle_help(msg: Message):
    text = (
        "<b>📖 Qo'llanma</b>\n\n"
        "<b>Qanday ishlaydi:</b>\n"
        "1. Har qanday media platformasidan URL yuboring\n"
        "2. Siz tanlagan formatni tanlang\n"
        "3. Bot yuklab olib, qayta ishlaydi va yuboradi\n\n"
        "<b>Format turlari:</b>\n"
        "🎬 <b>Video (MP4)</b> - To'liq video\n"
        "🎧 <b>Audio (MP3)</b> - Faqat ovoz\n"
        "🎞️ <b>GIF</b> - Animatsiyalı GIF\n"
        "🖼️ <b>Image</b> - Statik rasm\n\n"
        "<b>Masalalar yuz berganda:</b>\n"
        "• Link noto'g'ri bo'lishi mumkin\n"
        "• Kontent geo-bloklangan bo'lishi mumkin\n"
        "• Fayl juda katta bo'lishi mumkin\n"
        "• Server muammo bo'lishi mumkin\n\n"
        "<b>Proxies qo'shish:</b>\n"
        "app/proxies.txt fayliga proxy manzillarini qo'shing (har biri alohida qatorda)\n\n"
        "Savollar uchun: @support_admin"
    )
    await msg.answer(text)


async def handle_formats(msg: Message):
    text = (
        "<b>📋 Qo'llab-quvvatlanuvchi Formatlar</b>\n\n"
        "🎬 <b>Video (MP4)</b>\n"
        "   • Eng ko'p platformada ishlaydi\n"
        "   • H.264 kodeki bilan\n"
        "   • AAC audiosi bilan\n\n"
        "🎧 <b>Audio (MP3)</b>\n"
        "   • Faqat ovoz\n"
        "   • 192 kbps sifat\n"
        "   • Musiqalar uchun ideal\n\n"
        "🎞️ <b>GIF</b>\n"
        "   • Animatsiyalı GIF\n"
        "   • Kichik fayl o'lchami\n"
        "   • Qisqa videoular uchun\n\n"
        "🖼️ <b>Image (JPG/PNG)</b>\n"
        "   • Statik rasm\n"
        "   • Postlar va skrinshot uchun\n"
    )
    await msg.answer(text)


async def handle_link(msg: Message, state: FSMContext):
    url = (msg.text or "").strip()

    # Komandalar bo'lmasa, URL sifatida qayta ishlash
    if url.startswith("/"):
        return  # Komandalar uchun xalqaro handlers ishlatiladi

    # Foydalanuvchini database ga qo'shish/yangilash
    if not db.get_user(msg.from_user.id):
        db.add_user(
            msg.from_user.id,
            username=msg.from_user.username or "No username",
            first_name=msg.from_user.first_name or "",
            last_name=msg.from_user.last_name or "",
        )

    if not url or not is_supported_url(url):
        await msg.reply("❌ Link noto'g'ri yoki qo'llab-quvvatlanmaydi.\n/help buyrug'i bilan ko'proq ma'lumot oling.")
        return

    # URL ni save qilish
    await state.update_data(url=url)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Video", callback_data="format_video"),
            InlineKeyboardButton(text="🎧 Audio", callback_data="format_audio"),
        ],
        [
            InlineKeyboardButton(text="🎞️ GIF", callback_data="format_gif"),
            InlineKeyboardButton(text="🖼️ Image", callback_data="format_image"),
        ],
        [
            InlineKeyboardButton(text="📦 Hammasini", callback_data="format_both"),
        ]
    ])

    await msg.answer("📁 Qaysi formatda yuklaysiz?", reply_markup=keyboard)


async def handle_format_callback(callback: CallbackQuery, state: FSMContext):
    format_type_map = {
        "format_video": "video",
        "format_audio": "audio",
        "format_gif": "gif",
        "format_image": "image",
        "format_both": "both",
    }

    format_type = format_type_map.get(callback.data, "both")
    data = await state.get_data()
    url = data.get("url")

    if not url:
        await callback.answer("❌ URL topilmadi. Qayta urinib ko'ring.", show_alert=True)
        return

    # Download ni database ga log qilish
    download_id = db.log_download(
        callback.from_user.id,
        url,
        format_type,
        status="processing"
    )

    await callback.message.edit_text("⏳ Yuklab olish boshlandi... Bir oz kuting.")

    chat_dir = ensure_chat_dir(callback.message.chat.id)
    video_path: Path | None = None
    audio_path: Path | None = None

    try:
        video_path, audio_path, title = await download_video_and_audio(url, callback.message.chat.id, format_type)

        # Send video if available
        if video_path and video_path.exists():
            if MAX_UPLOAD_BYTES and video_path.stat().st_size > MAX_UPLOAD_BYTES:
                await callback.message.answer("⚠️ Video hajmi juda katta. Telegram cheklovisi.")
            else:
                video_file = FSInputFile(path=video_path)
                await callback.message.answer_video(video=video_file, caption=f"🎬 <b>{title}</b>")
                db.complete_download(download_id, video_path.stat().st_size)

        # Send audio if available
        if audio_path and audio_path.exists():
            if MAX_UPLOAD_BYTES and audio_path.stat().st_size > MAX_UPLOAD_BYTES:
                await callback.message.answer("⚠️ Audio hajmi juda katta. Sifatni kamaytirish kerak.")
            else:
                audio_file = FSInputFile(path=audio_path)
                await callback.message.answer_audio(audio=audio_file, caption=f"🎧 {title} — Audio (MP3)")

        if not video_path and not audio_path:
            await callback.message.answer("⚠️ Fayl yuklab olinolib, lekin xatolik yuz berdi.")
            db.fail_download(download_id, "File not created")

    except DownloadError as e:
        logger.exception("Download failed: %s", e)
        db.fail_download(download_id, str(e)[:200])
        await callback.message.answer(f"❌ Yuklab olish muvaffaqiyatsiz.\n\n{str(e)[:100]}")
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        db.fail_download(download_id, str(e)[:200])
        await callback.message.answer("💥 Kutilmagan xatolik yuz berdi. Keyinroq urinib ko'ring.")
    finally:
        with suppress(Exception):
            if video_path and video_path.parent.exists():
                cleanup_dir(video_path.parent)
            elif audio_path and audio_path.parent.exists():
                cleanup_dir(audio_path.parent)

        db.update_user_activity(callback.from_user.id)

    await callback.answer()


async def main() -> None:
    dp = Dispatcher()

    # Commands (BIRINCHI - highest priority)
    dp.message.register(handle_start, CommandStart())
    dp.message.register(handle_help, Command("help"))
    dp.message.register(handle_formats, Command("formats"))

    # Routers (admin va user panel)
    dp.include_router(admin_router)
    dp.include_router(logger_router)

    # Callbacks
    dp.callback_query.register(handle_format_callback, F.data.startswith("format_"))

    # Generic text handler (OXIRIDA - lowest priority)
    dp.message.register(handle_link, F.text)

    await on_startup()
    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    finally:
        await bot.session.close()
        await on_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
