from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram.types import Message

from src.services.db.data_access_module import upsert_member
from .main_handler import HandlerDeps

router = Router(name="setbio")
_deps: HandlerDeps


def setup(deps: HandlerDeps) -> None:
    global _deps
    _deps = deps


@router.message(Command("setbio"))
async def cmd_setbio(message: Message) -> None:
    if message.chat.type != ChatType.PRIVATE:
        return

    args = (message.text or "").split(maxsplit=1)
    bio = args[1].strip() if len(args) > 1 else ""
    if not bio:
        await message.answer("Используйте: /setbio <текст описания>")
        return

    async with _deps.session_factory() as session:
        m = await upsert_member(
            session,
            tg_user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
        m.bio = bio[:4000]
        await session.commit()

    await message.answer("Описание сохранено.")
