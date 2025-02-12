import logging
import os

from datetime import datetime, timedelta
from mailbox import Message
from typing import Union

import pytz
from aiogram.types import CallbackQuery
from aiogram.utils import markdown
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from humanfriendly.terminal import message

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased


from bd_api.middlewares.sa_tables import Subscription, subscriber, User
from utils.date_moscow import get_current_date
from utils.text_message import send_message

scheduler = AsyncIOScheduler()
logger = logging.getLogger(__name__)
load_dotenv()

# async def update_subscription_status(db_session: AsyncSession, user_id: int, new_status: str):
#
#     result = await db_session.execute(select(Subscription).where(Subscription.user_id == user_id))
#     subscription = result.scalars().first()
#
#     if subscription:
#         subscription.status = new_status
#         await db_session.commit()
#         logger.info(f"Статус подписки юзера {user_id} обновлена до '{new_status}'.")
#
#         return subscription.status
#     else:
#         logger.error(f"Subscription status is {new_status}")


async def notify_expiring_subscriptions(db_session: AsyncSession, bot):
    current_date = get_current_date(True)
    target_date = current_date + timedelta(days=3)

    # 1
    try:
        result = await db_session.execute(
            select(Subscription).where(Subscription.end_date == target_date)
        )
        expiring_subscriptions = result.scalars().all()

        for subscription in expiring_subscriptions:
                result = await db_session.execute(select(User.full_name).where(User.id == subscription.user_id))
                full_name = result.scalar()
                name = full_name if full_name else "уважаемый пользователь нашего сервиса"

                if full_name:
                    await send_message(
                        bot=bot,
                        chat_id=subscription.user_id,
                        text=f"👋 Здравствуйте {name}!\n\n"
                             f"⏰ Ваша подписка истекает через 3 дня ({markdown.hpre(subscription.end_date)}).\n"
                             f"Пожалуйста, продлите её, чтобы продолжать пользоваться сервисом."
                    )
                else:
                    logger.error('Ошибка получения full_name в блоке notify_expiring_subscriptions')

    except Exception as e:
        logger.error(f"Ошибка при проверке подписок, заканчивающихся через 3 дня: {e}")

    # 2
    try:
        expired_subscriptions = await db_session.execute(
            select(Subscription).where(Subscription.end_date <= current_date)
        )
        expired_subscriptions = expired_subscriptions.scalars().all()

        admin_id = os.getenv('ADMIN_ID')

        for subscription in expired_subscriptions:
            result = await db_session.execute(
                select(User.full_name).where(User.user_id == subscription.user_id)
            )
            full_name = result.scalar()

            if full_name:
                link = f"tg://user?id={subscription.user_id}"
                clickable_link = f"{full_name}"

                await send_message(
                    chat_id=admin_id,
                    text=f'У пользователя с ником {markdown.hlink(clickable_link , link)} закончилась подписка.',
                    bot=bot
                )

            result = await db_session.execute(select(Subscription).where(Subscription.user_id == subscription.user_id))
            check_result = result.scalars().first()

            if check_result:
                check_result.month = None
                check_result.start_date = None
                check_result.end_date = None
                check_result.status = "not active"
                await db_session.commit()

            await send_message(
                bot=bot,
                chat_id=subscription.user_id,
                text=f"⛓️‍💥 Ваша подписка завершилась ({markdown.hpre(subscription.end_date)})."
                     f" Пожалуйста, продлите её, чтобы снова пользоваться AMMO VPN.")
            await db_session.commit()

    except Exception as e:
        logger.error(f"Ошибка при проверке истекших подписок: {e}")


async def start_scheduler(bot, db_session: AsyncSession):
    scheduler.add_job(notify_expiring_subscriptions, 'interval', days=1, args=[db_session, bot])
    scheduler.start()