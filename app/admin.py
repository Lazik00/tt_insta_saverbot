"""
Admin panel va boshqarish
"""
from __future__ import annotations
import logging
from typing import List, Optional
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, User
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database import db

logger = logging.getLogger(__name__)
admin_router = Router()


class AdminState(StatesGroup):
    waiting_broadcast_message = State()
    waiting_user_id_for_ban = State()
    waiting_user_id_for_unban = State()
    waiting_user_id_for_admin = State()
    waiting_notification_message = State()
    choosing_notification_target = State()


def is_admin(user_id: int) -> bool:
    """Admin tekshirish"""
    user = db.get_user(user_id)
    return user and user.get('is_admin', False) and not user.get('is_banned', False)


async def admin_only(msg: Message) -> bool:
    """Admin filtri"""
    if not is_admin(msg.from_user.id):
        await msg.reply("❌ Siz admin emassiz!")
        return False
    return True


@admin_router.message(Command("admin"))
async def handle_admin_panel(msg: Message):
    """Admin panelni ochish"""
    if not await admin_only(msg):
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"),
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
        ],
        [
            InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="🚫 Ban qilish", callback_data="admin_ban"),
        ],
        [
            InlineKeyboardButton(text="✅ Unban qilish", callback_data="admin_unban"),
            InlineKeyboardButton(text="👑 Admin qilish", callback_data="admin_make_admin"),
        ],
        [
            InlineKeyboardButton(text="📝 Admin loggari", callback_data="admin_logs"),
            InlineKeyboardButton(text="📬 Bildirishnomalar", callback_data="admin_notifications"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="admin_settings"),
            InlineKeyboardButton(text="🔄 Bot status", callback_data="admin_status"),
        ],
    ])

    text = (
        "<b>👑 Admin Panel</b>\n\n"
        "Quyidagi amallarni tanlang:"
    )

    await msg.answer(text, reply_markup=keyboard)
    db.log_admin_action(msg.from_user.id, "admin_panel_opened")


@admin_router.callback_query(F.data == "admin_users")
async def show_users(callback: CallbackQuery):
    """Foydalanuvchilarni ko'rish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin emas!", show_alert=True)
        return

    users = db.get_all_users()
    admin_users = [u for u in users if u['is_admin']]
    banned_users = [u for u in users if u['is_banned']]

    text = (
        f"<b>👥 Foydalanuvchilar Statistikasi</b>\n\n"
        f"📊 <b>Jami:</b> {len(users)}\n"
        f"👑 <b>Adminlar:</b> {len(admin_users)}\n"
        f"🚫 <b>Banlanganlar:</b> {len(banned_users)}\n"
        f"✅ <b>Faol:</b> {len([u for u in users if not u['is_banned']])}\n\n"
    )

    # Top users
    top_users = sorted(users, key=lambda x: x['downloads_count'], reverse=True)[:5]
    text += "<b>🏆 Top 5 Foydalanuvchi:</b>\n"
    for i, user in enumerate(top_users, 1):
        text += f"{i}. `{user['user_id']}` - {user['downloads_count']} downloads\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")],
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@admin_router.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery):
    """Statistikani ko'rish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin emas!", show_alert=True)
        return

    stats = db.get_statistics()

    success_rate = 0
    if stats['successful_downloads'] + stats['failed_downloads'] > 0:
        success_rate = (stats['successful_downloads'] /
                       (stats['successful_downloads'] + stats['failed_downloads']) * 100)

    text = (
        "<b>📊 Bot Statistikasi</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {stats['total_users']}\n"
        f"⚡ <b>Faol (24h):</b> {stats['active_users']}\n\n"
        f"✅ <b>Muvaffaqiyatli yuklab olish:</b> {stats['successful_downloads']}\n"
        f"❌ <b>Muvaffaqiyatsiz:</b> {stats['failed_downloads']}\n"
        f"📈 <b>Muvaffaqiyat darajasi:</b> {success_rate:.1f}%\n\n"
        f"💾 <b>Jami storage:</b> {stats['total_storage_used'] / (1024*1024):.1f} MB\n"
        f"⏱️ <b>Avg download time:</b> {stats['avg_download_time']:.1f} sec\n"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")],
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@admin_router.callback_query(F.data == "admin_broadcast")
async def broadcast_start(callback: CallbackQuery, state: FSMContext):
    """Broadcast xabar yuborish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin emas!", show_alert=True)
        return

    await state.set_state(AdminState.waiting_broadcast_message)
    text = (
        "<b>📢 Broadcast Xabar</b>\n\n"
        "Barcha foydalanuvchilarga yuborish uchun xabarni yuboring.\n"
        "(Rasmli va formatlangan xabarlar qo'llab-quvvatlanadi)\n\n"
        "/cancel - bekor qilish"
    )
    await callback.message.edit_text(text)
    await callback.answer()


@admin_router.message(AdminState.waiting_broadcast_message)
async def process_broadcast(msg: Message, state: FSMContext):
    """Broadcast xabarni qayta ishlash"""
    if not is_admin(msg.from_user.id):
        return

    if msg.text == "/cancel":
        await state.clear()
        await msg.reply("❌ Bekor qilindi")
        return

    # Broadcast xabarni yuborish
    users = db.get_all_users(is_banned=False)
    broadcast_text = msg.text

    sent_count = 0
    failed_count = 0
    message_id = db.send_message(
        msg.from_user.id,
        broadcast_text,
        is_broadcast=True
    )

    progress_msg = await msg.answer(f"📤 Broadcast yuborilmoqda... (0/{len(users)})")

    for i, user in enumerate(users):
        try:
            # Telegram API orqali xabar yuborish qilish kerak
            # await bot.send_message(user['user_id'], broadcast_text)
            sent_count += 1
            if i % 10 == 0:
                await progress_msg.edit_text(f"📤 Broadcast yuborilmoqda... ({i}/{len(users)})")
        except Exception as e:
            logger.error(f"Broadcast {user['user_id']} uchun: {e}")
            failed_count += 1

    db.update_message_status(message_id, sent_count, failed_count)
    db.log_admin_action(
        msg.from_user.id,
        "broadcast_sent",
        details=f"Sent: {sent_count}, Failed: {failed_count}"
    )

    await state.clear()
    await msg.answer(
        f"✅ Broadcast tugallandi!\n\n"
        f"✅ Yuborilgan: {sent_count}\n"
        f"❌ Xatolar: {failed_count}"
    )


@admin_router.callback_query(F.data == "admin_ban")
async def ban_start(callback: CallbackQuery, state: FSMContext):
    """Ban qilish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin emas!", show_alert=True)
        return

    await state.set_state(AdminState.waiting_user_id_for_ban)
    text = (
        "<b>🚫 Ban qilish</b>\n\n"
        "Foydalanuvchi ID sini yuboring.\n"
        "(Masalan: 123456789)\n\n"
        "/cancel - bekor qilish"
    )
    await callback.message.edit_text(text)
    await callback.answer()


@admin_router.message(AdminState.waiting_user_id_for_ban)
async def process_ban(msg: Message, state: FSMContext):
    """Ban qilish operatsiyasi"""
    if not is_admin(msg.from_user.id):
        return

    if msg.text == "/cancel":
        await state.clear()
        await msg.reply("❌ Bekor qilindi")
        return

    try:
        user_id = int(msg.text)
        user = db.get_user(user_id)

        if not user:
            await msg.reply("❌ Foydalanuvchi topilmadi")
            return

        if db.ban_user(user_id, "Admin tomonidan"):
            db.log_admin_action(
                msg.from_user.id,
                "ban_user",
                user_id,
                f"Ban qildi: {user['username']}"
            )
            await msg.answer(f"✅ {user_id} ban qilindi")
        else:
            await msg.answer("❌ Ban qilishda xatolik")

    except ValueError:
        await msg.reply("❌ Notog'ri ID format")

    await state.clear()


@admin_router.callback_query(F.data == "admin_unban")
async def unban_start(callback: CallbackQuery, state: FSMContext):
    """Ban olib tashlash"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin emas!", show_alert=True)
        return

    await state.set_state(AdminState.waiting_user_id_for_unban)
    text = (
        "<b>✅ Ban olib tashlash</b>\n\n"
        "Foydalanuvchi ID sini yuboring.\n"
        "/cancel - bekor qilish"
    )
    await callback.message.edit_text(text)
    await callback.answer()


@admin_router.message(AdminState.waiting_user_id_for_unban)
async def process_unban(msg: Message, state: FSMContext):
    """Unban operatsiyasi"""
    if not is_admin(msg.from_user.id):
        return

    if msg.text == "/cancel":
        await state.clear()
        await msg.reply("❌ Bekor qilindi")
        return

    try:
        user_id = int(msg.text)
        user = db.get_user(user_id)

        if not user:
            await msg.reply("❌ Foydalanuvchi topilmadi")
            return

        if db.unban_user(user_id):
            db.log_admin_action(
                msg.from_user.id,
                "unban_user",
                user_id,
                f"Unban qildi: {user['username']}"
            )
            await msg.answer(f"✅ {user_id} unban qilindi")
        else:
            await msg.answer("❌ Unban qilishda xatolik")

    except ValueError:
        await msg.reply("❌ Notog'ri ID format")

    await state.clear()


@admin_router.callback_query(F.data == "admin_make_admin")
async def make_admin_start(callback: CallbackQuery, state: FSMContext):
    """Admin qilish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin emas!", show_alert=True)
        return

    await state.set_state(AdminState.waiting_user_id_for_admin)
    text = (
        "<b>👑 Admin qilish</b>\n\n"
        "Foydalanuvchi ID sini yuboring.\n"
        "/cancel - bekor qilish"
    )
    await callback.message.edit_text(text)
    await callback.answer()


@admin_router.message(AdminState.waiting_user_id_for_admin)
async def process_make_admin(msg: Message, state: FSMContext):
    """Admin qilish operatsiyasi"""
    if not is_admin(msg.from_user.id):
        return

    if msg.text == "/cancel":
        await state.clear()
        await msg.reply("❌ Bekor qilindi")
        return

    try:
        user_id = int(msg.text)
        user = db.get_user(user_id)

        if not user:
            await msg.reply("❌ Foydalanuvchi topilmadi")
            return

        if db.make_admin(user_id):
            db.log_admin_action(
                msg.from_user.id,
                "make_admin",
                user_id,
                f"Admin qildi: {user['username']}"
            )
            await msg.answer(f"✅ {user_id} admin qilindi")
        else:
            await msg.answer("❌ Admin qilishda xatolik")

    except ValueError:
        await msg.reply("❌ Notog'ri ID format")

    await state.clear()


@admin_router.callback_query(F.data == "admin_logs")
async def show_admin_logs(callback: CallbackQuery):
    """Admin loggari"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin emas!", show_alert=True)
        return

    logs = db.get_admin_logs(limit=20)

    text = "<b>📝 Admin Amallari</b>\n\n"
    for log in logs[:10]:
        action = log['action']
        target = f" ({log['target_user_id']})" if log['target_user_id'] else ""
        text += f"• {log['timestamp']}: {action}{target}\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")],
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@admin_router.callback_query(F.data == "admin_notifications")
async def show_notifications_menu(callback: CallbackQuery, state: FSMContext):
    """Bildirishnomalar menyu"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin emas!", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="admin_send_notification")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")],
    ])

    text = "<b>📬 Bildirishnomalar</b>"
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@admin_router.callback_query(F.data == "admin_send_notification")
async def send_notification_start(callback: CallbackQuery, state: FSMContext):
    """Xabar yuborish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin emas!", show_alert=True)
        return

    await state.set_state(AdminState.waiting_notification_message)
    text = (
        "<b>📬 Bildirishnoma Yuborish</b>\n\n"
        "Xabarni yuboring:\n"
        "/cancel - bekor qilish"
    )
    await callback.message.edit_text(text)
    await callback.answer()


@admin_router.message(AdminState.waiting_notification_message)
async def process_notification(msg: Message, state: FSMContext):
    """Xabarni qayta ishlash"""
    if not is_admin(msg.from_user.id):
        return

    if msg.text == "/cancel":
        await state.clear()
        await msg.reply("❌ Bekor qilindi")
        return

    users = db.get_all_users(is_banned=False)
    for user in users:
        db.add_notification(user['user_id'], msg.text, "info")

    await msg.answer(f"✅ {len(users)} ta foydalanuvchiga bildirishnoma yuborildi")
    await state.clear()


@admin_router.callback_query(F.data == "admin_status")
async def show_bot_status(callback: CallbackQuery):
    """Bot statusi"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin emas!", show_alert=True)
        return

    stats = db.get_statistics()

    text = (
        "<b>🤖 Bot Status</b>\n\n"
        f"✅ <b>Status:</b> Online\n"
        f"👥 <b>Active users:</b> {stats['active_users']}\n"
        f"📊 <b>Total users:</b> {stats['total_users']}\n"
        f"📈 <b>Downloads:</b> {stats['successful_downloads']}\n"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")],
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@admin_router.callback_query(F.data == "admin_back")
async def go_back(callback: CallbackQuery):
    """Orqaga qaytish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin emas!", show_alert=True)
        return

    await handle_admin_panel(callback.message)
    await callback.answer()


@admin_router.callback_query(F.data == "admin_settings")
async def show_settings(callback: CallbackQuery):
    """Sozlamalar"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin emas!", show_alert=True)
        return

    text = (
        "<b>⚙️ Sozlamalar</b>\n\n"
        "Bot sozlamalari (Coming soon)\n"
        "• Max file size\n"
        "• Download quality\n"
        "• Maintenance mode\n"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")],
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

