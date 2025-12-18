"""
Callbacks bilan ishlovchi komandalar
"""
from __future__ import annotations
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

logger = logging.getLogger(__name__)


async def handle_cancel_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Bekor qilish"""
    await state.clear()
    await callback.message.edit_text("❌ Bekor qilindi.")
    await callback.answer()


async def handle_info_callback(callback: CallbackQuery) -> None:
    """Batafsil ma'lumot"""
    text = (
        "ℹ️ <b>Bot Haqida</b>\n\n"
        "Bu bot Telegram orasida 50+ platformadan media yuklab oladi.\n\n"
        "<b>Imkonyatlari:</b>\n"
        "• Video, Audio, GIF, Rasm yuklab olish\n"
        "• Turli formatda konversiya\n"
        "• Proxy qo'llab-quvvatlash\n"
        "• Tez va samarali\n\n"
        "<b>Versiya:</b> 2.0.0\n"
        "<b>Muallif:</b> Laziz\n"
        "<b>Litsenziya:</b> MIT"
    )
    await callback.message.answer(text)
    await callback.answer()

