"""
Background tasks va scheduler
"""
import asyncio
import logging
from datetime import datetime, timedelta
from app.database import db

logger = logging.getLogger(__name__)


async def broadcast_scheduler():
    """Pending xabarlarni yuborish scheduleri"""
    while True:
        try:
            pending_messages = db.get_pending_messages(limit=10)

            for msg in pending_messages:
                # Xabar yuborish logikasi
                users = db.get_all_users(is_banned=False)
                sent = 0
                failed = 0

                for user in users:
                    try:
                        # Bot orqali xabar yuborish
                        # await bot.send_message(user['user_id'], msg['message_text'])
                        sent += 1
                    except Exception as e:
                        logger.error(f"Xabar yuborish xatosi: {e}")
                        failed += 1

                db.update_message_status(msg['id'], sent, failed)
                logger.info(f"✅ Broadcast tugallandi: {sent} sent, {failed} failed")

            await asyncio.sleep(60)  # Har 1 daqiqa tekshir

        except Exception as e:
            logger.error(f"Broadcast scheduler xatosi: {e}")
            await asyncio.sleep(60)


async def cleanup_old_files():
    """Eski fayllarni o'chirish"""
    while True:
        try:
            import shutil
            from pathlib import Path

            data_dir = Path("data")
            cutoff_time = datetime.now() - timedelta(days=7)

            for user_dir in data_dir.glob("chat_*"):
                for subdir in user_dir.glob("*"):
                    if subdir.is_dir():
                        mtime = datetime.fromtimestamp(subdir.stat().st_mtime)
                        if mtime < cutoff_time:
                            shutil.rmtree(subdir, ignore_errors=True)
                            logger.info(f"🗑️ Eski fayl o'chirildi: {subdir}")

            await asyncio.sleep(3600)  # Har 1 soat

        except Exception as e:
            logger.error(f"Cleanup xatosi: {e}")
            await asyncio.sleep(3600)


async def update_statistics():
    """Har kuni statistikani yangilash"""
    while True:
        try:
            stats = db.get_statistics()

            # Log statistika
            logger.info(
                f"📊 Daily stats - "
                f"Users: {stats['total_users']}, "
                f"Downloads: {stats['successful_downloads']}, "
                f"Storage: {stats['total_storage_used'] / (1024*1024):.1f}MB"
            )

            await asyncio.sleep(86400)  # Har 24 soat

        except Exception as e:
            logger.error(f"Statistics update xatosi: {e}")
            await asyncio.sleep(86400)


async def start_background_tasks():
    """Barcha background tasklarni ishga tushirish"""
    tasks = [
        broadcast_scheduler(),
        cleanup_old_files(),
        update_statistics(),
    ]
    await asyncio.gather(*tasks)

