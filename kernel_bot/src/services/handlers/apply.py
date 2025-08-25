from __future__ import annotations
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.markdown import hbold, hlink, hcode

from sqlalchemy import select

from src.texts.texts import WELCOME_TEXT
from src.services.db.data_access_module import get_member, get_pending_app, create_app
from .main_handler import HandlerDeps

router = Router(name="apply")
_deps: HandlerDeps


def setup(deps: HandlerDeps) -> None:
    global _deps
    _deps = deps


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    if message.chat.type != ChatType.PRIVATE:
        return
    await message.answer(WELCOME_TEXT)


@router.message(Command("apply"))
async def cmd_apply(message: Message, bot: Bot) -> None:
    if message.chat.type != ChatType.PRIVATE:
        return

    async with _deps.session_factory() as session:
        member = await get_member(session, message.from_user.id)
        if member is not None:
            await message.answer("Вы уже участник { K E R N E L }.")
            return

        app = await get_pending_app(session, message.from_user.id)
        if app is None:
            app = await create_app(session, message.from_user.id)
            await session.commit()

        user_link = hlink(message.from_user.full_name, f"tg://user?id={message.from_user.id}")
        text = (
            f"Новая заявка в {hbold('{ K E R N E L }')}\n"
            f"Пользователь: {user_link}\n"
            f"username: {hcode('@' + message.from_user.username) if message.from_user.username else '—'}\n"
            f"id: {message.from_user.id}\n\n"
            f"Что сделать с заявкой?"
        )

        await bot.send_message(
            chat_id=_deps.admin_user_id,
            text=text,
            reply_markup=_kb_yes_no(str(app.id)),
            disable_web_page_preview=True,
        )
        await message.answer("Заявка создана и отправлена на модерацию. Ожидайте решения администратора.")


def _kb_yes_no(app_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve:{app_id}"),
                InlineKeyboardButton(text="🗑️ Отклонить", callback_data=f"deny:{app_id}"),
            ]
        ]
    )
