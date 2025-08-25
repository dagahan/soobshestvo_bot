from __future__ import annotations
from aiogram import Router
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus

from src.services.db.data_access_module import remove_member
from .main_handler import HandlerDeps

router = Router(name="on_left_member")
_deps: HandlerDeps


def setup(deps: HandlerDeps) -> None:
    global _deps
    _deps = deps


@router.on_left_member()
async def on_chat_member(update: ChatMemberUpdated) -> None:
    if update.chat.id != _deps.group_chat_id:
        return

    new_state = update.new_chat_member
    if new_state.status in {ChatMemberStatus.LEFT, ChatMemberStatus.KICKED, ChatMemberStatus.BANNED}:
        target_user_id = getattr(new_state, "user", None).id if getattr(new_state, "user", None) else None
        if target_user_id is None:
            return

        async with _deps.session_factory() as session:
            await remove_member(session, target_user_id)
            await session.commit()



