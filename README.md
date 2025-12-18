# TikTok, Instagram, YouTube Video Downloader Bot 🤖

Telegram bot uchun multimedia kontenti TikTok, Instagram Reels va YouTube-dan yuklab olish.

## 🌟 Xususiyatlar

- ✅ **TikTok** videolari yuklab olish
- ✅ **Instagram Reels** yuklab olish
- ✅ **YouTube** videolari yuklab olish
- ✅ **Avtomatik audio ajratish** (MP3 format)
- ✅ **Admin panel** - foydalanuvchilarni boshqarish
- ✅ **Premium tizimi** - ixcham foydalanuvchilar
- ✅ **Statistika tracking** - yuklab olishlar va foydalanuvchilar soni
- ✅ **SQLite database** - barcha ma'lumotlarni saqlash
- ✅ **O'zbek tili** - to'liq UI

## 📦 O'rnatish

### Talablar
- Python 3.10+
- pip
- FFmpeg (audio ajratish uchun)

### Qadamlar

1. **Repository klonlash**
```bash
git clone <repo-url>
cd tt_insta_saverbot
```

2. **Virtual muhit yaratish**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Dependensiyalar o'rnatish**
```bash
pip install -r requirements.txt
```

4. **FFmpeg o'rnatish** (agar o'rnatilmagan bo'lsa)
```bash
# Windows:
choco install ffmpeg

# yoki manual: https://ffmpeg.org/download.html
```

5. **.env faylini sozlash**
```bash
copy .env.example .env
```

`.env` faylida:
```
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
ADMIN_ID=5773429637
DATA_DIR=data
MAX_UPLOAD_BYTES=0
```

6. **Botni ishga tushirish**
```bash
python -m app.main
```

## 🎮 Foydalanish

### Oddiy foydalanuvchilarga buyruqlar
- Har qanday TikTok/Instagram/YouTube linkni yuboring
- Bot video (MP4) va audio (MP3) yuklab beradi

### Admin buyruqlari
- `/admin` - Admin panel ochish
- `/premium <user_id>` - Foydalanuvchiga premium berish
- `/revoke <user_id>` - Premiumni bekor qilish
- `/userinfo <user_id>` - Foydalanuvchi ma'lumotlarini ko'rish
- `/stats` - Statistikani ko'rish

## 📊 Admin Panel

Admin (5773429637) quyidagi funksiyalardan foydalana oladi:

- 📊 **Statistika** - Jami foydalanuvchilar va yuklab olishlar soni
- 👑 **Premium berish** - Foydalanuvchiga premium huquqlari berish
- ❌ **Premium bekor qilish** - Premiumni olib tashlash
- 📈 **Foydalanuvchi info** - Individual foydalanuvchi ma'lumotlarini ko'rish

## 📁 Loyaha struktura

```
tt_insta_saverbot/
├── app/
│   ├── main.py           # Asosiy bot logikasi
│   ├── admin.py          # Admin panel
│   ├── database.py       # Veritabanı operatsiyalari
│   ├── utils.py          # Yordamchi funktrsiyalar
│   ├── validators.py     # URL validatsiyasi
│   └── __init__.py
├── data/
│   └── bot.db            # SQLite database
├── requirements.txt      # Python dependensiyalari
├── .env.example          # Muhit sozlamalari shabloni
└── README.md
```

## 🔧 Konfiguratsiya

### Environment o'zgaruvchilari

| O'zgaruvchi | Tavsif | Qiymat |
|-------------|--------|--------|
| `BOT_TOKEN` | Telegram Bot tokeni | - |
| `ADMIN_ID` | Admin Telegram ID | `5773429637` |
| `DATA_DIR` | Ma'lumotlar katalogi | `data` |
| `MAX_UPLOAD_BYTES` | Maksimal fayl hajmi (0 = cheksiz) | `0` |

## 🛡️ Xavfsizlik

- ⚠️ Faqat o'zingizga tegishli kontentni yuklab oling
- 🔒 Admin ID sizning ID raqamingizga o'zgartirilsinganiga ishonch hosil qiling
- 🔐 `.env` faylini hech kim ko'rmagani uchun saqlang

## 📋 Qo'llab-quvvatlanadigan saytlar

- `tiktok.com` / `vt.tiktok.com`
- `instagram.com` (Reels va videolar)
- `youtube.com` / `youtu.be`

## 🐛 Muammolar va takliflar

Agar xatolikka duch kelsangiz yoki taklif bo'lsa, GitHub issue yarating.

## 📝 Litsenziya

MIT License - batafsil uchun `LICENSE` faylini ko'ring.

---

**Tayyorlagan:** Laziz  
**Admin ID:** 5773429637

