from __future__ import annotations
from aiogram import Router, Bot
from aiogram.types import ChatJoinRequest

from src.services.db.data_access_module import (
    invite_by_link,
    remove_all_apps_for_user,
    upsert_member,
)
from .main_handler import HandlerDeps

router = Router(name="join_request")
_deps: HandlerDeps


def setup(deps: HandlerDeps) -> None:
    global _deps
    _deps = deps


@router.chat_join_request()
async def on_join_request(req: ChatJoinRequest, bot: Bot) -> None:
    user_id = req.from_user.id
    if req.invite_link is None:
        await bot.decline_chat_join_request(chat_id=req.chat.id, user_id=user_id)
        return

    async with _deps.session_factory() as session:
        inv = await invite_by_link(session, req.invite_link.invite_link)
        if inv is None or inv.is_revoked or inv.chat_id != _deps.group_chat_id:
            await bot.decline_chat_join_request(chat_id=req.chat.id, user_id=user_id)
            return

        if user_id != inv.intended_user_id:
            await bot.decline_chat_join_request(chat_id=req.chat.id, user_id=user_id)
            try:
                await bot.ban_chat_member(chat_id=req.chat.id, user_id=user_id)
            except Exception:
                pass
            try:
                await bot.revoke_chat_invite_link(chat_id=req.chat.id, invite_link=inv.invite_link)
            except Exception:
                pass
            inv.is_revoked = True
            await session.commit()
            return

        await bot.approve_chat_join_request(chat_id=req.chat.id, user_id=user_id)
        try:
            await bot.revoke_chat_invite_link(chat_id=req.chat.id, invite_link=inv.invite_link)
        except Exception:
            pass
        inv.is_revoked = True

        await upsert_member(
            session,
            tg_user_id=user_id,
            username=req.from_user.username,
            first_name=req.from_user.first_name,
            last_name=req.from_user.last_name,
        )
        await remove_all_apps_for_user(session, user_id)
        await session.commit()

        try:
            await bot.send_message(chat_id=user_id, text="Добро пожаловать в { K E R N E L }!")
        except Exception:
            pass



