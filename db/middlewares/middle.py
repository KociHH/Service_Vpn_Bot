import asyncio
import logging
from aiogram import BaseMiddleware, Bot
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import Callable, Any
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select
from datetime import datetime
from db.tables import Subscription, User
from settings import BotParams
from keyboards.inline_keyboard.common import Main_menu
from aiogram.utils.keyboard import InlineKeyboardBuilder

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


class CheckSubcription(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker):
        super().__init__()
        self.session_factory = session_factory

    async def _check_channel_subscription(self, bot: Bot, user_id: int, channel_username: str) -> bool:
        try:
            channel_id = f"@{channel_username}" if not channel_username.startswith('@') else channel_username
            logger.info(f"Проверяем подписку пользователя {user_id} на канал {channel_id}")
            
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            is_subscribed = member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
            
            logger.info(f"Статус пользователя {user_id} в канале {channel_id}: {member.status}, подписан: {is_subscribed}")
            return is_subscribed
            
        except TelegramBadRequest as e:
            logger.error(f"Ошибка при проверке подписки пользователя {user_id}: {e}")
            return True
        except Exception as e:
            logger.error(f"Неожиданная ошибка при проверке подписки: {e}")
            return True

    async def _send_subscription_message(self, bot: Bot, user_id: int, channel_username: str):
        builder = InlineKeyboardBuilder()
        
        clean_username = channel_username.replace('@', '')
        channel_url = f"https://t.me/{clean_username}"
        
        builder.button(
            text="Подписаться на канал",
            url=channel_url
        )
        
        try:
            await bot.send_message(
                chat_id=user_id,
                text="🔔 Для использования бота необходимо подписаться на наш канал!",
                reply_markup=builder.as_markup()
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения о подписке пользователю {user_id}: {e}")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, str | Any], Any],
        event: TelegramObject,
        data: str | Any,
    ) -> Any:
        bot: Bot = data.get("bot")
        
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id if event.from_user else None
            
            logger.info(f"Middleware CheckSubcription: обрабатываем пользователя {user_id}")
            
            if user_id and BotParams.username_channel:
                logger.info(f"Проверяем подписку пользователя {user_id} на канал {BotParams.username_channel}")
                
                is_subscribed = await self._check_channel_subscription(
                    bot, user_id, BotParams.username_channel
                )
                
                logger.info(f"Результат проверки подписки для пользователя {user_id}: {is_subscribed}")
                
                if not is_subscribed:
                    logger.info(f"Пользователь {user_id} не подписан, отправляем сообщение")
                    await self._send_subscription_message(
                        bot, user_id, BotParams.username_channel
                    )
                    return None
                else:
                    logger.info(f"Пользователь {user_id} подписан, пропускаем дальше")
            else:
                logger.info(f"Пропускаем проверку: user_id={user_id}, channel={BotParams.username_channel}")

        async with self.session_factory() as session:
            data["db_session"] = session
            result = await handler(event, data)
            await session.commit()
            return result