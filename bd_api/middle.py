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


# class RemoveKeyboardMiddleware(BaseMiddleware):
#     async def __call__(
#             self,
#             handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
#             event: Message,
#             data: Dict[str, Any]
#     ) -> Any:
#         # Выполняем оригинальный обработчик
#         result = await handler(event, data)
#
#         # Удаляем клавиатуру после выполнения команды
#         if isinstance(event, Message) and event.text and event.text.startswith('/'):
#             await event.answer(
#                 "клавиатура удалена",  # Невидимый символ
#                 reply_markup=ReplyKeyboardRemove()
#             )
#         return result
#
#
# def setup_middleware(dp):
#     # Регистрируем middleware для всех сообщений
#     dp.message.middleware(RemoveKeyboardMiddleware())





# async def main():
#     global connection
#     try:
#         connection = psycopg2.connect(
#             host=host,
#             user=user,
#             password=password,
#             database=db_name,
#         )
#         connection.autocommit = True
#         cursor = connection.cursor()
#         cursor.execute(
#             "SELECT version();"
#         )
#         print(f'Server version: {cursor.fetchone()}')
#
#         cursor = connection.cursor()
#         cursor.execute(
#             """CREATE TABLE IF NOT EXISTS users(
#             id serial PRIMARY KEY,
#             first_name VARCHAR(255) NOT NULL,
#             nickname VARCHAR(255) NOT NULL);"""
#         )
#         print('Data created')
#         cursor = connection.cursor()
#         cursor.execute("""
#         INSERT INTO users(first_name, nickname)
#         VALUES ('oleg', 'hohlova');
#
#
#         INSERT INTO users(first_name, nickname)
#         VALUES ('sex', 'penis');
#
#
#         INSERT INTO users(first_name, nickname)
#         VALUES ('chel', 'popka');
# """)
#
#         cursor = connection.cursor()
#         cursor.execute(
#             """SELECT nickname FROM users
#             WHERE first_name = 'oleg';""")
#         cursor = connection.cursor()
#         print(cursor.fetchone())
#
#         # cursor = connection.cursor()
#         # cursor.execute(
#         #     """DROP TABLE users"""
#         # )
#         print("Users deleted")
#     except Exception as e:
#         print(e)


# if __name__ == '__main__':
#     asyncio.run(main())