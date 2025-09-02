import logging
from celery_.celery_app import celery_app
import asyncio
import logging
import os
from datetime import datetime, timedelta
from utils.other import currently_msk
from aiogram.utils import markdown
from dotenv import load_dotenv
from db.tables import Subscription, User, user_dao, sub_dao
from utils.text_message import send_message
from aiogram import Bot
from settings import BotParams
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

logger = logging.getLogger(__name__)
load_dotenv()
admin_id = os.getenv('ADMIN_ID')

@celery_app.task
def notify_expiring_subscriptions():
    print("_________________________________________NOTIFY_EXPIRING_SUBSCRIPTIONS_________________________________________")
    end_log = "_______________________________________________________________________________________________________________"
    bot = Bot(token=BotParams.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    async def _async(bot):
        target_date = currently_msk + timedelta(days=3)
        sended = 0
    # 1
        try:
            expiring_subscriptions = await sub_dao.get_all(Subscription.end_date == target_date)

            for subscription in expiring_subscriptions:
                user = await user_dao.get_one(User.user_id == subscription.user_id)
                user_id = user.user_id
                await send_message(
                    bot=bot,
                    chat_id=subscription.user_id,
                    text=(
                        f"👋 Здравствуйте! \n"
                        f"⏰ Ваша подписка истекает через 3 дня ({markdown.hpre(subscription.end_date)}).\n"
                        f"Пожалуйста, продлите её, чтобы продолжать пользоваться сервисом."
                    ))
                logger.info(f"У юзера {user_id} заканчивается подписка через 3 дня.")
                sended += 1
                if sended == 10:
                    await asyncio.sleep(5)
                    sended = 0

        except Exception as e:
            logger.error(f"Ошибка при проверке подписок, заканчивающихся через 3 дня: {e}")
            print(end_log)
            
    # 2
        try:
            expired_subscriptions = await sub_dao.get_all(Subscription.end_date <= currently_msk)

            for subscription in expired_subscriptions:
                user = await user_dao.get_one(User.user_id == subscription.user_id)
                user_id = user.user_id
                link = f"tg://user?id={subscription.user_id}"
                await send_message(
                    chat_id=admin_id,
                    text=f'У пользователя {markdown.hlink(str(user_id), link)} закончилась подписка.',
                    bot=bot
                    )

                await sub_dao.delete(Subscription.user_id == subscription.user_id)
                logger.info(f"У юзера {user_id} закончилась подписка.")
                logger.info('Истекшая подписка удалена.')

                await send_message(
                    bot=bot,
                    chat_id=subscription.user_id,
                    text=(
                        f"⛓️‍💥 Ваша подписка завершилась ({markdown.hpre(subscription.end_date)}).\n"
                        f"Пожалуйста, продлите её, чтобы снова пользоваться {BotParams.name_project} VPN."
                    ))
                sended += 5
                if sended == 10:
                    await asyncio.sleep(5)
                    sended = 0

            logger.info("Истекшие подписки обработаны.")
            print(end_log)
        except Exception as e:
            logger.error(f"Ошибка при проверке истекших подписок: {e}")
            print(end_log)

    asyncio.run(_async(bot))

