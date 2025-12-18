"""
Config va konfiguratsiya
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Bot konfiguratsiyasi
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
    print("⚠️ OGOHLANTIRISH: BOT_TOKEN .env fayliga qo'shilishi kerak!")
    print("📝 .env fayliga o'z Telegram bot tokenini kiriting")
    # Hozircha dummy token, production da error beradi
    BOT_TOKEN = None

# Fayl saqlanadigan katalog
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Maksimal fayl o'lcham (baytda)
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", "2097152000"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Support admini (ixtiyoriy)
SUPPORT_ADMIN = os.getenv("SUPPORT_ADMIN", "@admin")

# Yuklab olish parametrlari
DOWNLOAD_TIMEOUT = 300  # 5 daqiqa
MAX_RETRIES = 3
RETRY_DELAY = 2

# Rasm sifati (0-100)
THUMBNAIL_QUALITY = 85
IMAGE_QUALITY = 90

# Audio sifati (kbps)
AUDIO_BITRATE = "192k"

# Video formatlar
VIDEO_FORMAT = "bv*+ba/b[ext=mp4]/b"
VIDEO_MERGE_FORMAT = "mp4"

# yt-dlp parametrlari
YDL_QUIET = True
YDL_NO_WARNINGS = True

