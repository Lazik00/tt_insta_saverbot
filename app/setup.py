"""
Bot setup va initialization
"""
import logging
from app.database import db

logger = logging.getLogger(__name__)


def init_admin(admin_id: int = None):
    """Default admin qo'shish"""
    # .env dan yoki hardcoded
    default_admin_id = admin_id or 123456789

    # Admin user qo'shish
    existing = db.get_user(default_admin_id)
    if not existing:
        db.add_user(
            default_admin_id,
            username="admin",
            first_name="Admin",
            last_name="User",
            is_admin=True
        )
        logger.info(f"✅ Admin qo'shildi: {default_admin_id}")
    else:
        if not existing.get('is_admin'):
            db.make_admin(default_admin_id)
            logger.info(f"✅ {default_admin_id} admin qilindi")


def setup_database():
    """Database sozlash"""
    logger.info("🔧 Database sozlanmoqda...")

    # Database tables allaqachon init_db orqali yaratilgan
    stats = db.get_statistics()
    logger.info(f"📊 Current stats: {stats}")

    # Default admin qo'shish (optional)
    # init_admin(1234567890)  # O'z admin ID ni qo'shing


async def on_bot_startup():
    """Bot ishga tushganida"""
    logger.info("🚀 Bot starting...")
    setup_database()
    logger.info("✅ Bot ready!")


async def on_bot_shutdown():
    """Bot to'xtalganda"""
    logger.info("🛑 Bot stopping...")

