
import asyncio
import logging

from settings import SQl_localhost, SQL_URL
from aiogram import BaseMiddleware
from sqlalchemy import select, pool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject, CallbackQuery, Message, ReplyKeyboardRemove


logger = logging.getLogger(__name__)

sql_data = SQL_URL()
engine = create_async_engine(sql_data.get('DATABASE_URL_PUBLIC_TIMEWEB'), future=True, echo=False, poolclass=pool.NullPool, connect_args={"ssl": "require"})
async_session = async_sessionmaker(engine, expire_on_commit=False,  class_=AsyncSession)


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker):
        super().__init__()
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Any],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_factory() as session:
            data["db_session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception as e:
                    await session.rollback()
                    logger.error(f"Ошибка при обработке запроса: {e}")
                    raise Exception(f'Ошибка при обработке запроса: {e}') from e
