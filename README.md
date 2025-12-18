# 🎬 Ko'p Platformali Media Yuklovchi Bot

Telegram bot bo'lib, 50+ ta turli platformalardan video, audio va boshqa media kontentini yuklab oladi.

## ✨ Xususiyatlar

- ✅ **50+ platformani qo'llash**: TikTok, Instagram, YouTube, Facebook, Twitter/X, Twitch, Pinterest, Reddit, Snapchat, Dailymotion, Vimeo, Bluesky, LinkedIn, SoundCloud va boshqalar
- 🎬 **Video yuklab olish** (MP4 formatida)
- 🎧 **Audio chiqarish** (MP3 formatida)
- 🎞️ **GIF yaratish** (animatsiyalı)
- 🖼️ **Rasm olish** (JPG/PNG)
- 🔄 **Avtomatik qayta urinish** (Tekshirish bilan)
- 🌐 **Proxy qo'llab-quvvatlash** (blokirov'ni chetga suring)
- ⚡ **Async operatsiyalar** (tez va samarali)
- 📊 **Juda ko'p funksiya** (formatlashni tanlash, yordam, info)

## 🚀 O'rnatish

### 1. Repozitoriyani klonlash
```bash
git clone <repository_url>
cd tt_insta_saverbot
```

### 2. Virtual muhitni yaratish
```bash
python -m venv venv
venv\Scripts\activate  # Windows uchun
source venv/bin/activate  # Linux/Mac uchun
```

### 3. Dependenciyalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. ffmpeg o'rnatish
```bash
# Windows (choco bilan)
choco install ffmpeg

# Linux
sudo apt-get install ffmpeg

# Mac
brew install ffmpeg
```

### 5. .env faylini yaratish
```bash
echo BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN" > .env
echo DATA_DIR="data" >> .env
echo MAX_UPLOAD_BYTES="2097152000" >> .env
```

Telegram BotFather orqali token oling: https://t.me/BotFather

## 📋 Konfiguratsiya

### .env fayli
```env
BOT_TOKEN=6123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz1234567890
DATA_DIR=data
MAX_UPLOAD_BYTES=2097152000  # Telegram cheklov (2GB)
```

### Proxies qo'shish
`app/proxies.txt` fayliga proxy manzillarini qo'shing:
```
http://proxy1.com:8080
http://proxy2.com:8080
socks5://proxy3.com:1080
```

## 🎯 Ishlatish

### Botni ishga tushirish
```bash
python -m app.main
```

### Telegram komandalar
- `/start` - Bot haqida ma'lumot
- `/help` - Batafsil qo'llanma
- `/formats` - Qo'llab-quvvatlanuvchi formatlar

### Funksionalligi
1. Istalgan platformanig linkini yuboring
2. Format turini tanlang (Video/Audio/GIF/Image)
3. Bot yuklab olib, qayta ishlaydi va yuboradi

## 🔧 Qo'llab-quvvatlanuvchi Platformalar

| Platform | Video | Audio | Qo'llab-quvvatlash |
|----------|-------|-------|-------------------|
| TikTok | ✅ | ✅ | To'liq |
| Instagram | ✅ | ✅ | To'liq |
| YouTube | ✅ | ✅ | To'liq |
| Facebook | ✅ | ✅ | To'liq |
| Twitter/X | ✅ | ✅ | To'liq |
| Twitch | ✅ | ✅ | Clipslar |
| Pinterest | ✅ | ✅ | Videolar |
| Reddit | ✅ | ✅ | To'liq |
| Snapchat | ✅ | ✅ | QR orqali |
| Dailymotion | ✅ | ✅ | To'liq |
| Vimeo | ✅ | ✅ | To'liq |
| Bluesky | ✅ | ✅ | To'liq |
| LinkedIn | ✅ | ✅ | To'liq |
| SoundCloud | ✅ | ✅ | Audio |
| Spotify | ✅ | ✅ | Audio |

## 📦 Dependenciyalar

- **aiogram** (3.12.0) - Telegram bot framework
- **yt-dlp** (2025.9.21) - Media yuklab olish
- **python-dotenv** (1.0.1) - .env fayl o'qish
- **aiohttp** (3.9.1) - Async HTTP
- **Pillow** (10.1.0) - Rasm ishlash
- **ffmpeg-python** (0.2.1) - Audio/Video qayta ishlash
- **requests** (2.31.0) - HTTP sorovlar

## 🐛 Muammolarni hal qilish

### "ffmpeg not found"
- ffmpeg o'rnatilgan ekanligini tekshiring
- `ffmpeg -version` buyrug'ini ishga tushiring

### "Video yuklab olinolib, lekin xatolik yuz berdi"
- Internet ulanishni tekshiring
- Proxy qo'shib ko'ring
- Link aktiv ekanligini tekshiring

### "Kontent geo-bloklangan"
- Proxies.txt fayliga proxy qo'shing
- VPN ishlatib ko'ring

## 📝 Logglar

Bot logglar konsolga chiqaradi. Muammolarni debug qilish uchun log chiqarish darajasini o'zgartiring:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 🔐 Xavfsizlik

⚠️ **Muhim:** Faqat o'zingizga tegishli yoki ruxsat etilgan kontentni yuklab oling!

## 📄 Litsenziya

MIT License

## 👨‍💻 Muallif

Laziz (2025)

## 🤝 Hissa qo'shish

Xatolarni bildirsang yoki tavsiyalar qo'shgan bo'lsan, issues yoki pull requests ochishni istovdo qilamiz!

---

**Savol yoki muammolar?** GitHub issuelerini ochib qo'ying yoki admin bilan bog'laning.

