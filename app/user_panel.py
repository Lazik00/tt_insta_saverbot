"""
Foydalanuvchi profili va xabarlar
"""
from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database import db

logger_router = Router()


class UserState(StatesGroup):
    pass


@logger_router.message(Command("profile"))
async def show_profile(msg: Message):
    """Foydalanuvchi profili"""
    user = db.get_user(msg.from_user.id)

    if not user:
        # Yangi foydalanuvchi qo'shish
        db.add_user(
            msg.from_user.id,
            username=msg.from_user.username or "No username",
            first_name=msg.from_user.first_name or "",
            last_name=msg.from_user.last_name or "",
        )
        user = db.get_user(msg.from_user.id)

    downloads = db.get_user_downloads(msg.from_user.id, limit=5)

    storage_mb = user['storage_used'] / (1024 * 1024)

    text = (
        "<b>👤 Sizning Profil</b>\n\n"
        f"👤 <b>ID:</b> `{user['user_id']}`\n"
        f"📛 <b>Username:</b> @{user['username'] or 'N/A'}\n"
        f"📝 <b>Ism:</b> {user['first_name']} {user['last_name'] or ''}\n\n"
        f"📊 <b>Statistika:</b>\n"
        f"⬇️ <b>Jami yuklab olish:</b> {user['downloads_count']}\n"
        f"💾 <b>Storage ishlatilgan:</b> {storage_mb:.1f} MB\n"
        f"📅 <b>Ro'yxatdan o'tgan:</b> {user['join_date']}\n"
        f"⏰ <b>Oxirgi faoliyat:</b> {user['last_activity']}\n\n"
    )

    if downloads:
        text += "<b>🕐 Oxirgi yuklab olishlari:</b>\n"
        for d in downloads:
            status = "✅" if d['status'] == "completed" else "❌"
            text += f"{status} {d['title'][:30]} - {d['format']}\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 Bildirishnomalar", callback_data="user_notifications")],
        [InlineKeyboardButton(text="📜 Tarix", callback_data="user_history")],
        [InlineKeyboardButton(text="📞 Support", callback_data="user_support")],
    ])

    await msg.answer(text, reply_markup=keyboard)
    db.update_user_activity(msg.from_user.id)


@logger_router.callback_query(F.data == "user_notifications")
async def show_notifications(callback: CallbackQuery):
    """Bildirishnomalarni ko'rish"""
    notifications = db.get_unread_notifications(callback.from_user.id)

    if not notifications:
        text = "✅ Yangi bildirishnomalar yo'q"
    else:
        text = "<b>📬 Sizning Bildirishnomalaringiz</b>\n\n"
        for notif in notifications[:10]:
            text += f"• {notif['message']}\n   {notif['created_at']}\n\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="user_back")],
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@logger_router.callback_query(F.data == "user_history")
async def show_history(callback: CallbackQuery):
    """Download tarixini ko'rish"""
    downloads = db.get_user_downloads(callback.from_user.id, limit=20)

    if not downloads:
        text = "📜 Hali hech qanday yuklab olish yo'q"
    else:
        text = "<b>📜 Download Tarixingiz</b>\n\n"
        for d in downloads[:10]:
            status_icon = "✅" if d['status'] == "completed" else "❌"
            size_str = f"{d['file_size'] / (1024*1024):.1f} MB" if d['file_size'] else "N/A"
            text += (
                f"{status_icon} <b>{d['title'][:40]}</b>\n"
                f"   Format: {d['format']} | Size: {size_str}\n"
                f"   {d['download_time']}\n\n"
            )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="user_back")],
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@logger_router.callback_query(F.data == "user_support")
async def show_support(callback: CallbackQuery):
    """Support ma'lumotlari"""
    text = (
        "<b>📞 Support</b>\n\n"
        "Muammolar yoki savollar uchun:\n"
        "• GitHub issues: <link>\n"
        "• Telegram: @admin\n"
        "• Email: support@example.com\n\n"
        "/help - Qo'llanma\n"
        "/formats - Formatlar haqida\n"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="user_back")],
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@logger_router.callback_query(F.data == "user_back")
async def user_back(callback: CallbackQuery):
    """Profillga qaytish"""
    user = db.get_user(callback.from_user.id)

    if not user:
        await callback.answer("❌ Profil topilmadi", show_alert=True)
        return

    downloads = db.get_user_downloads(callback.from_user.id, limit=5)
    storage_mb = user['storage_used'] / (1024 * 1024)

    text = (
        "<b>👤 Sizning Profil</b>\n\n"
        f"👤 <b>ID:</b> `{user['user_id']}`\n"
        f"📛 <b>Username:</b> @{user['username'] or 'N/A'}\n"
        f"📝 <b>Ism:</b> {user['first_name']}\n\n"
        f"📊 <b>Statistika:</b>\n"
        f"⬇️ <b>Jami yuklab olish:</b> {user['downloads_count']}\n"
        f"💾 <b>Storage:</b> {storage_mb:.1f} MB\n"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 Bildirishnomalar", callback_data="user_notifications")],
        [InlineKeyboardButton(text="📜 Tarix", callback_data="user_history")],
        [InlineKeyboardButton(text="📞 Support", callback_data="user_support")],
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@logger_router.message(Command("mydownloads"))
async def show_my_downloads(msg: Message):
    """O'zimning yuklab olishlari"""
    downloads = db.get_user_downloads(msg.from_user.id, limit=50)

    if not downloads:
        await msg.answer("📜 Hali hech qanday yuklab olish yo'q")
        return

    text = "<b>📜 Sizning Yuklab Olishlari</b>\n\n"

    completed = len([d for d in downloads if d['status'] == 'completed'])
    failed = len([d for d in downloads if d['status'] == 'failed'])

    text += f"✅ Muvaffaqiyatli: {completed}\n"
    text += f"❌ Xatolar: {failed}\n\n"

    for d in downloads[:15]:
        status_icon = "✅" if d['status'] == "completed" else "❌"
        text += f"{status_icon} {d['title'][:40]} ({d['format']})\n"

    await msg.answer(text)


@logger_router.message(Command("stats"))
async def show_user_stats(msg: Message):
    """Foydalanuvchi statistikasi"""
    user = db.get_user(msg.from_user.id)

    if not user:
        db.add_user(msg.from_user.id)
        user = db.get_user(msg.from_user.id)

    downloads = db.get_user_downloads(msg.from_user.id, limit=100)

    completed = len([d for d in downloads if d['status'] == 'completed'])
    failed = len([d for d in downloads if d['status'] == 'failed'])

    # Format statistikasi
    format_stats = {}
    for d in downloads:
        fmt = d['format']
        format_stats[fmt] = format_stats.get(fmt, 0) + 1

    text = (
        "<b>📊 Sizning Statistikalaringiz</b>\n\n"
        f"📥 <b>Jami yuklab olish:</b> {user['downloads_count']}\n"
        f"✅ <b>Muvaffaqiyatli:</b> {completed}\n"
        f"❌ <b>Muvaffaqiyatsiz:</b> {failed}\n"
        f"💾 <b>Storage ishlatilgan:</b> {user['storage_used'] / (1024*1024):.1f} MB\n\n"
    )

    if format_stats:
        text += "<b>📋 Format statistikasi:</b>\n"
        for fmt, count in sorted(format_stats.items(), key=lambda x: x[1], reverse=True):
            text += f"• {fmt}: {count}\n"

    await msg.answer(text)

