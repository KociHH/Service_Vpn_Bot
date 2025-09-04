import logging
from celery_.celery_app import celery_app
import asyncio
import logging
import os
from datetime import datetime, timedelta
from utils.other import currently_msk
from aiogram.utils import markdown
from dotenv import load_dotenv
from db.tables import Subscription, User
from aiogram import Bot
from settings import BotParams
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from db.middlewares.middle import async_session as async_session_factory
from keyboards.inline_keyboard.main_inline_keyboard import Extend_kb

logger = logging.getLogger(__name__)
load_dotenv()
admin_id = os.getenv('ADMIN_ID')

@celery_app.task
def notify_expiring_subscriptions():
    print("_________________________________________NOTIFY_EXPIRING_SUBSCRIPTIONS_________________________________________")
    end_log = "_______________________________________________________________________________________________________________"
    bot = Bot(token=BotParams.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    async def _async(bot: Bot, db_session: AsyncSession):
        user_dao = BaseDAO(User, db_session)
        sub_dao = BaseDAO(Subscription, db_session)
        target_date = currently_msk + timedelta(days=3)
        target_date = target_date.date()
        end_date = Subscription.end_date.date()

        sended = 0
        limit_send = 10
        # истекает через 3 дня
        try:
            checked_users = 0
            expiring_subscriptions = await sub_dao.get_all(end_date == target_date.date())

            for subscription in expiring_subscriptions:
                user = await user_dao.get_one(User.user_id == subscription.user_id)
                user_id = user.user_id
                await bot.send_message(
                    chat_id=subscription.user_id,
                    text=
                        f"👋 Здравствуйте! \n"
                        f"⏰ Ваша подписка истекает через {markdown.hbold("3")} дня ({markdown.hpre(subscription.end_date)}).\n"
                        f"Пожалуйста, продлите её, чтобы продолжать пользоваться сервисом.",
                    reply_markup=Extend_kb(True)
                    )
                logger.info(f"У юзера {user_id} заканчивается подписка через 3 дня.")
                sended += 1
                checked_users += 1
                if sended == limit_send:
                    await asyncio.sleep(5)
                    sended = 0

            logger.info(f"Истекающие подписки {checked_users} юзеров успешно обработаны")
        except Exception as e:
            logger.error(f"Ошибка при проверке подписок, заканчивающихся через 3 дня: {e}")
            print(end_log)
            
        # истеченные     
        try:
            checked_users = 0
            expired_subscriptions = await sub_dao.get_all(Subscription.end_date <= currently_msk)

            for subscription in expired_subscriptions:
                user = await user_dao.get_one(User.user_id == subscription.user_id)
                user_id = user.user_id
                link = f"tg://user?id={subscription.user_id}"
                await bot.send_message(
                    chat_id=admin_id,
                    text=f'У пользователя {markdown.hlink(str(user_id), link)} закончилась подписка.',
                    )

                await sub_dao.delete(Subscription.user_id == subscription.user_id)
                logger.info(f"У юзера {user_id} закончилась подписка.")
                logger.info('Истекшая подписка удалена.')

                await bot.send_message(
                    chat_id=subscription.user_id,
                    text=
                        f"⛓️‍💥 Ваша подписка истекла.\n"
                        f"Пожалуйста, продлите её, чтобы снова пользоваться {BotParams.name_project} VPN.",
                    reply_markup=Extend_kb(False)
                    )
                sended += 1
                checked_users += 1
                if sended == limit_send:
                    await asyncio.sleep(5)
                    sended = 0

            logger.info(f"Истекшие подписки {checked_users} юзеров успешно обработаны")
            print(end_log)
        except Exception as e:
            logger.error(f"Ошибка при проверке истекших подписок: {e}")
            print(end_log)
    
    async def run_celery_task():
        async with async_session_factory() as session:
            await _async(bot, session)
    asyncio.run(run_celery_task())

