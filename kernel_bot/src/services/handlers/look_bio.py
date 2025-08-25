from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from src.services.db.data_access_module import member_by_username
from .main_handler import HandlerDeps

router = Router(name="look_bio")
_deps: HandlerDeps


def setup(deps: HandlerDeps) -> None:
    global _deps
    _deps = deps


@router.message(Command("look_bio"))
async def cmd_look_bio(message: Message) -> None:
    if message.chat.type != ChatType.PRIVATE:
        return

    args = (message.text or "").split(maxsplit=1)
    raw = args[1].strip() if len(args) > 1 else ""
    if not raw:
        await message.answer("Используйте: /look_bio <username>")
        return

    username = raw.lstrip("@")
    async with _deps.session_factory() as session:
        m = await member_by_username(session, username)
        if m is None:
            await message.answer("Участник не найден в базе.")
            return

        name = " ".join(x for x in [m.first_name, m.last_name] if x)
        text = f"{hbold(name or '@' + username)}\nusername: @{m.username or username}\n\n{m.bio or '—'}"
        await message.answer(text)
