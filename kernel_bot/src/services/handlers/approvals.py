from __future__ import annotations
import uuid
from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, delete

from src.services.db.models import Application
from src.services.db.data_access_module import create_personal_invite, approve_app
from .main_handler import HandlerDeps

router = Router(name="approvals")
_deps: HandlerDeps


def setup(deps: HandlerDeps) -> None:
    global _deps
    _deps = deps


@router.callback_query(F.data.startswith("approve:"))
async def cb_approve(call: CallbackQuery, bot: Bot) -> None:
    app_id = uuid.UUID(call.data.split(":", 1)[1])

    async with _deps.session_factory() as session:
        res = await session.execute(select(Application).where(Application.id == app_id))
        app = res.scalar_one_or_none()
        if app is None:
            await call.answer("Заявка не найдена", show_alert=True)
            return

        inv = await create_personal_invite(
            session,
            bot=bot,
            chat_id=_deps.group_chat_id,
            intended_user_id=app.tg_user_id,
        )
        link_str = inv.invite_link
        await approve_app(session, app, inv.id)
        await session.commit()

    await bot.send_message(
        app.tg_user_id,
        text=(
            "Ваша персональная ссылка на вступление в { K E R N E L } (24 часа, одноразовая).\n\n"
            f"{link_str}\n\n"
            "Важно: это join-request — нажмите «Запросить вступление»."
        ),
    )
    await call.answer("Одобрено")


@router.callback_query(F.data.startswith("deny:"))
async def cb_deny(call: CallbackQuery) -> None:
    app_id = uuid.UUID(call.data.split(":", 1)[1])
    async with _deps.session_factory() as session:
        await session.execute(delete(Application).where(Application.id == app_id))
        await session.commit()
    await call.answer("Отклонено")
