import asyncio
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


from bd_api.middlewares.sa_tables import Subscription, subscriber, User, UserUpdater
from utils.date_moscow import get_current_date
from utils.text_message import send_message

scheduler = AsyncIOScheduler()
logger = logging.getLogger(__name__)
load_dotenv()

admin_id = os.getenv('ADMIN_ID')
async def notify_expiring_subscriptions(db_session: AsyncSession, bot):
    current_date = get_current_date(True)
    print(current_date)
    target_date = current_date + timedelta(days=3)

    # 1
    try:
        result = await db_session.execute(
            select(User.full_name, Subscription)
            .join(Subscription, User.user_id == Subscription.user_id)
            .where(Subscription.end_date == target_date)
        )
        expiring_subscriptions = result.all()
        for full_name, subscription in expiring_subscriptions:
            name = full_name if full_name else "пользователь AMMO VPN"
            await send_message(
                bot=bot,
                chat_id=subscription.user_id,
                text=(
                    f"👋 Здравствуйте {name}! \n"
                    f"⏰ Ваша подписка истекает через 3 дня ({markdown.hpre(subscription.end_date)}).\n"
                    f"Пожалуйста, продлите её, чтобы продолжать пользоваться сервисом."
                )
            )
            await asyncio.sleep(0.5)

    except Exception as e:
        logger.error(f"Ошибка при проверке подписок, заканчивающихся через 3 дня: {e}")

    # 2
    try:
            result = await db_session.execute(
                select(User.full_name, Subscription)
                .join(Subscription, User.user_id == Subscription.user_id)
                .where(Subscription.end_date <= current_date)
            )
            expired_subscriptions = result.all()
            for full_name, subscription in expired_subscriptions:
                link = f"tg://user?id={subscription.user_id}"
                clickable_link = full_name if full_name else "Неизвестный пользователь"
                await send_message(
                    chat_id=admin_id,
                    text=f'У пользователя {markdown.hlink(clickable_link, link)} закончилась подписка.',
                    bot=bot
                )

                update = UserUpdater(
                    subscription,
                    {
                        'month': None,
                        'start_date': None,
                        'end_date': None,
                        'status': "not active"
                    }
                )
                await update.save_to_db(db_session)

                await send_message(
                    bot=bot,
                    chat_id=subscription.user_id,
                    text=(
                        f"⛓️‍💥 Ваша подписка завершилась ({markdown.hpre(subscription.end_date)}).\n"
                        f"Пожалуйста, продлите её, чтобы снова пользоваться AMMO VPN."
                    )
                )
                await asyncio.sleep(0.5)

            logger.info("Истекшие подписки обработаны.")
    except Exception as e:
        logger.error(f"Ошибка при проверке истекших подписок: {e}")


async def start_scheduler(bot, db_session: AsyncSession):
    scheduler.add_job(notify_expiring_subscriptions, 'cron', hour=12, minute=0, args=[db_session, bot])
    scheduler.start()