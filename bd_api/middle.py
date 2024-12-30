import asyncio
import logging
from settings import SQlpg
from aiogram import BaseMiddleware
from sqlalchemy import select, pool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject, CallbackQuery, Message, ReplyKeyboardRemove

logger = logging.getLogger(__name__)


postgres_url = SQlpg(path='.env')

engine = create_async_engine(postgres_url, future=True, echo=False, poolclass=pool.NullPool)
async_session = async_sessionmaker(engine, expire_on_commit=False,  class_=AsyncSession)

# Сreating a midleware for asynchronous connection Potgres
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



# if __name__ == '__main__':
#     asyncio.run(main())
