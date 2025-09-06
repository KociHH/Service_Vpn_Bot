import asyncio
import logging
from aiogram import BaseMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import Callable, Any
from aiogram.types import TelegramObject
import logging

logger = logging.getLogger(__name__)


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker):
        super().__init__()
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, str | Any], Any],
        event: TelegramObject,
        data: str | Any,
    ) -> Any:
        async with self.session_factory() as session:
            data["db_session"] = session
            result = await handler(event, data)
            await session.commit()
            return result
