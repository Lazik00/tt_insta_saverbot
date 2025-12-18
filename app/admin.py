from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import os
from app.database import (
    get_total_downloads, get_total_users, set_premium,
    is_premium, get_user_download_count, add_user
)

ADMIN_ID = int(os.getenv("ADMIN_ID", "5773429637"))

admin_router = Router()


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Get admin panel keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👑 Premium Berish", callback_data="admin_premium")],
        [InlineKeyboardButton(text="❌ Premium Bekor Qilish", callback_data="admin_revoke_premium")],
        [InlineKeyboardButton(text="📈 Foydalanuvchi Info", callback_data="admin_user_info")],
        [InlineKeyboardButton(text="🔙 Ortga", callback_data="admin_close")],
    ])


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == ADMIN_ID


@admin_router.message(Command("admin"))
async def admin_panel(msg: Message):
    """Open admin panel"""
    if not is_admin(msg.from_user.id):
        await msg.answer("❌ Sizda admin huquqlari yo'q.")
        return

    text = "🔧 <b>Admin Panel</b>\n\nQuyidagi amallardan birini tanlang:"
    await msg.answer(text, reply_markup=get_admin_keyboard())


@admin_router.callback_query(F.data == "admin_stats")
async def admin_stats(query: CallbackQuery):
    """Show statistics"""
    if not is_admin(query.from_user.id):
        await query.answer("❌ Sizda admin huquqlari yo'q.", show_alert=True)
        return

    total_downloads = await get_total_downloads()
    total_users = await get_total_users()

    text = (
        "<b>📊 Bot Statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
        f"⬇️ Jami yuklab olishlar: <b>{total_downloads}</b>\n"
    )

    await query.message.edit_text(text, reply_markup=get_admin_keyboard())
    await query.answer()


@admin_router.callback_query(F.data == "admin_premium")
async def admin_premium_prompt(query: CallbackQuery):
    """Prompt for premium user ID"""
    if not is_admin(query.from_user.id):
        await query.answer("❌ Sizda admin huquqlari yo'q.", show_alert=True)
        return

    text = "👑 <b>Premium Berish</b>\n\nFoydalanuvchi ID raqamini yuboring:"
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Ortga", callback_data="admin_back")]
    ]))
    await query.answer()


@admin_router.callback_query(F.data == "admin_revoke_premium")
async def admin_revoke_premium_prompt(query: CallbackQuery):
    """Prompt for revoking premium"""
    if not is_admin(query.from_user.id):
        await query.answer("❌ Sizda admin huquqlari yo'q.", show_alert=True)
        return

    text = "❌ <b>Premium Bekor Qilish</b>\n\nFoydalanuvchi ID raqamini yuboring:"
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Ortga", callback_data="admin_back")]
    ]))
    await query.answer()


@admin_router.callback_query(F.data == "admin_user_info")
async def admin_user_info_prompt(query: CallbackQuery):
    """Prompt for user info"""
    if not is_admin(query.from_user.id):
        await query.answer("❌ Sizda admin huquqlari yo'q.", show_alert=True)
        return

    text = "📈 <b>Foydalanuvchi Ma'lumotlari</b>\n\nFoydalanuvchi ID raqamini yuboring:"
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Ortga", callback_data="admin_back")]
    ]))
    await query.answer()


@admin_router.callback_query(F.data == "admin_back")
async def admin_back(query: CallbackQuery):
    """Return to admin panel"""
    if not is_admin(query.from_user.id):
        await query.answer("❌ Sizda admin huquqlari yo'q.", show_alert=True)
        return

    text = "🔧 <b>Admin Panel</b>\n\nQuyidagi amallardan birini tanlang:"
    await query.message.edit_text(text, reply_markup=get_admin_keyboard())
    await query.answer()


@admin_router.callback_query(F.data == "admin_close")
async def admin_close(query: CallbackQuery):
    """Close admin panel"""
    await query.message.delete()
    await query.answer("✅ Panel yopildi.")


@admin_router.message(Command("premium"))
async def set_premium_cmd(msg: Message):
    """Admin command: /premium <user_id>"""
    if not is_admin(msg.from_user.id):
        await msg.answer("❌ Sizda admin huquqlari yo'q.")
        return

    try:
        parts = msg.text.split()
        if len(parts) < 2:
            await msg.answer("❌ Foydalanish: /premium <user_id>")
            return

        user_id = int(parts[1])
        await add_user(user_id)
        await set_premium(user_id, True)
        await msg.answer(f"✅ Foydalanuvchi {user_id} premium qilindi.")
    except ValueError:
        await msg.answer("❌ ID raqam noto'g'ri.")
    except Exception as e:
        await msg.answer(f"❌ Xatolik: {str(e)}")


@admin_router.message(Command("revoke"))
async def revoke_premium_cmd(msg: Message):
    """Admin command: /revoke <user_id>"""
    if not is_admin(msg.from_user.id):
        await msg.answer("❌ Sizda admin huquqlari yo'q.")
        return

    try:
        parts = msg.text.split()
        if len(parts) < 2:
            await msg.answer("❌ Foydalanish: /revoke <user_id>")
            return

        user_id = int(parts[1])
        await set_premium(user_id, False)
        await msg.answer(f"✅ Foydalanuvchi {user_id} premium bekor qilindi.")
    except ValueError:
        await msg.answer("❌ ID raqam noto'g'ri.")
    except Exception as e:
        await msg.answer(f"❌ Xatolik: {str(e)}")


@admin_router.message(Command("userinfo"))
async def user_info_cmd(msg: Message):
    """Admin command: /userinfo <user_id>"""
    if not is_admin(msg.from_user.id):
        await msg.answer("❌ Sizda admin huquqlari yo'q.")
        return

    try:
        parts = msg.text.split()
        if len(parts) < 2:
            await msg.answer("❌ Foydalanish: /userinfo <user_id>")
            return

        user_id = int(parts[1])
        download_count = await get_user_download_count(user_id)
        premium = await is_premium(user_id)

        premium_status = "Ha" if premium else "Yo'q"
        text = (
            f"<b>Foydalanuvchi {user_id} Ma'lumotlari</b>\n\n"
            f"⬇️ Yuklab olishlar soni: <b>{download_count}</b>\n"
            f"👑 Premium: <b>{premium_status}</b>\n"
        )

        await msg.answer(text)
    except ValueError:
        await msg.answer("❌ ID raqam noto'g'ri.")
    except Exception as e:
        await msg.answer(f"❌ Xatolik: {str(e)}")

