from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Iterable

from aiogram import Dispatcher, Router, Bot, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllPrivateChats,
    Message,
)
from aiogram.types.error_event import ErrorEvent
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@dataclass(frozen=True)
class HandlerDeps:
    session_factory: async_sessionmaker[AsyncSession]
    group_chat_id: int
    admin_user_id: int


class MainHandler:
    def __init__(self) -> None:
        self.main_router = Router(name="root")
        

    def include_command_routers(self, deps: HandlerDeps) -> None:
        from . import apply, approvals, on_left_member, join_request, setbio, look_bio
        command_modules = (apply, approvals, on_left_member, join_request, setbio, look_bio)

        for m in command_modules:
            if hasattr(m, "setup"):
                m.setup(deps)
            self.main_router.include_router(m.router)


    def attach_fallbacks(self) -> None:
        fallback = Router(name="fallback")

        @fallback.message(F.text.startswith("/"))
        async def unknown_command(msg: Message) -> None:
            await msg.answer("Неизвестная команда. Открой /help или напиши /apply.")

        @root_router.errors()
        async def on_error(event: ErrorEvent) -> None:
            logging.exception("Unhandled error in handler", exc_info=event.exception)
            upd = event.update
            if isinstance(upd, Message):
                try:
                    await upd.answer("Упс, что-то пошло не так. Уже чиним.")
                except Exception:
                    pass

        root_router.include_router(fallback) 


    async def setup_bot_commands(self, bot: Bot) -> None:
        await bot.set_my_commands(
            commands=[
                BotCommand(command="apply",  description="Подать заявку на вступление"),
                BotCommand(command="setbio", description="Задать описание о себе"),
                BotCommand(command="look_bio",  description="Посмотреть описание участника"),
                BotCommand(command="help",   description="Справка"),
            ],
            scope=BotCommandScopeAllPrivateChats(),
        )


    def make_dispatcher(self, *, deps: HandlerDeps) -> Dispatcher:
        dp = Dispatcher(storage=MemoryStorage())
        self.include_command_routers(deps)
        self.attach_fallbacks()
        dp.include_router(root_router)
        return dp



        