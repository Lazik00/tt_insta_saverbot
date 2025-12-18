"""
ENV va Admin Configuration Verify
"""
import os
from pathlib import Path
from dotenv import load_dotenv

print("=" * 70)
print("🔍 ENVIRONMENT CONFIGURATION VERIFICATION")
print("=" * 70)

# Load .env
load_dotenv()

# Configuration Check
configs = {
    "BOT_TOKEN": os.getenv("BOT_TOKEN"),
    "DATA_DIR": os.getenv("DATA_DIR", "data"),
    "MAX_UPLOAD_BYTES": os.getenv("MAX_UPLOAD_BYTES", "2097152000"),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    "SUPPORT_ADMIN": os.getenv("SUPPORT_ADMIN", "@admin"),
    "ADMIN_ID": os.getenv("ADMIN_ID", "5773429637"),
}

print("\n1️⃣ ENVIRONMENT VARIABLES:")
print("-" * 70)
for key, value in configs.items():
    if key == "BOT_TOKEN":
        if value and not value.startswith("YOUR_"):
            token_preview = value[:20] + "..." if len(value) > 20 else value
            print(f"   ✅ {key:20} = {token_preview}")
        else:
            print(f"   ❌ {key:20} = NOT SET OR TEMPLATE")
    else:
        print(f"   ✅ {key:20} = {value}")

# .env file check
print("\n2️⃣ .ENV FILE CHECK:")
print("-" * 70)
env_file = Path(".env")
if env_file.exists():
    with open(env_file) as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    print(f"   ✅ .env file exists")
    print(f"   ✅ {len(lines)} configuration lines")
    for line in lines:
        if "=" in line:
            key = line.split("=")[0]
            print(f"      • {key}")
else:
    print(f"   ❌ .env file not found")

# Database check
print("\n3️⃣ DATABASE CHECK:")
print("-" * 70)
from app.database import db

admin_id = int(configs["ADMIN_ID"])
user = db.get_user(admin_id)

if user:
    print(f"   ✅ Admin user exists in database")
    print(f"      User ID: {user['user_id']}")
    print(f"      Username: {user['username']}")
    print(f"      Is Admin: {'✅ YES' if user['is_admin'] else '❌ NO'}")
    print(f"      Is Banned: {'❌ YES' if user['is_banned'] else '✅ NO'}")
else:
    print(f"   ❌ Admin user NOT in database")

# Admin function check
print("\n4️⃣ ADMIN FUNCTION CHECK:")
print("-" * 70)
from app.admin import is_admin

admin_check = is_admin(admin_id)
print(f"   is_admin({admin_id}) = {'✅ TRUE' if admin_check else '❌ FALSE'}")

# Router check
print("\n5️⃣ ROUTER CHECK:")
print("-" * 70)
try:
    from app.admin import admin_router
    print(f"   ✅ Admin router imported successfully")
except Exception as e:
    print(f"   ❌ Admin router import error: {e}")

# Main module check
print("\n6️⃣ MAIN MODULE CHECK:")
print("-" * 70)
try:
    from app.main import bot, main
    print(f"   ✅ Main module imported successfully")
    print(f"   ✅ Bot instance created")
except Exception as e:
    print(f"   ❌ Main module error: {e}")

# Final Summary
print("\n" + "=" * 70)
print("✅ SUMMARY")
print("=" * 70)

all_ok = (
    configs["BOT_TOKEN"] and not configs["BOT_TOKEN"].startswith("YOUR_") and
    user and user.get('is_admin') and
    admin_check
)

if all_ok:
    print("✅ BARCHA KONFIGURATSIYALAR TO'G'RI!")
    print("\n🚀 Bot ishga tushirish uchun:")
    print("   python -m app.main")
    print("\n📱 Telegram botda:")
    print("   /admin - admin panel uchun")
else:
    print("❌ MUAMMOLAR BORA:")
    if not configs["BOT_TOKEN"]:
        print("   • BOT_TOKEN .env da yo'q")
    if not user:
        print("   • Admin user database da yo'q")
    if user and not user.get('is_admin'):
        print("   • Admin user admin emas")
    if not admin_check:
        print("   • is_admin() function FALSE")

print("\n" + "=" * 70)

