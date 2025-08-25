from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from src.core.utils import EnvTools
from src.services.db.database import DataBase
from src.services.handlers.main_handler import MainHandler, HandlerDeps


class KernelBot:
    def __init__(self) -> None:
        self.token = EnvTools.required_load_env_var("BOT_TOKEN")
        self.group_chat_id = int(EnvTools.required_load_env_var("KERNEL_CHAT_ID"))
        self.admin_user_id = int(EnvTools.required_load_env_var("ADMIN_USER_ID"))
        self.db = DataBase()
        self.bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        self.main_handler = MainHandler()


    async def _prepare(self) -> None:
        await self.db.init_alchemy_engine()

        self.bot = Bot(token=self.token)
        self.dp = self.main_handler.make_dispatcher(
            deps=HandlerDeps(
                session_factory=self.db.async_session,  # type: ignore[arg-type]
                group_chat_id=self.group_chat_id,
                admin_user_id=self.admin_user_id,
            )
        )
        await self.main_handler.setup_bot_commands(self.bot)


    async def run(self) -> None:
        await self._prepare()
        assert self.bot and self.dp
        await self.dp.start_polling(
            self.bot,
            allowed_updates=["message", "callback_query", "chat_join_request", "chat_member"],
        )


