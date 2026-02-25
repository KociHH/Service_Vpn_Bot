import logging
from celery_habitat.celery_app import celery_app
import asyncio
import logging
import os
from datetime import datetime, timedelta
from utils.work import currently_msk
from aiogram.utils import markdown
from dotenv import load_dotenv
from db.tables import Subscription, User, TrialSubscription, VlessLinks
from aiogram import Bot
from settings import BotParams
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from db.tables import async_session as async_session_factory
from keyboards.inline_keyboard.common import Extend_kb
from sqlalchemy import func
from utils.work import admin_id

logger = logging.getLogger(__name__)
load_dotenv()

@celery_app.task
def notify_expiring_subscriptions():
    print("_________________________________________NOTIFY_EXPIRING_SUBSCRIPTIONS_________________________________________")
    end_log = "_______________________________________________________________________________________________________________"
    
    async def _async():
        bot = Bot(token=BotParams.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        
        try:
            async with async_session_factory() as db_session:
                sub_dao = BaseDAO(Subscription, db_session)
                trial_dao = BaseDAO(TrialSubscription, db_session)
                target_date = currently_msk() + timedelta(days=3)
                target_date = target_date.date()

                # истекает через 3 дня (только обычные подписки)
                try:
                    checked_users = 0
                    expiring_subscriptions = await sub_dao.get_all_column_values(
                        columns=(Subscription.user_id, Subscription.end_date),
                        where=func.date(Subscription.end_date) == target_date)

                    for user in expiring_subscriptions:
                        user_id = user[0]
                        end_date = user[1]

                        logger.info(f"У юзера {user_id} заканчивается подписка через 3 дня.")
                        await bot.send_message(
                            chat_id=user_id,
                            text=
                                f"👋 Здравствуйте!\n\n"
                                f"⏰ Срок действия вашей подписки истекает через {markdown.hbold("3")} дня, в {markdown.hcode(end_date)} по мск.\n"
                                f"Просим продлить её, чтобы продолжать пользоваться нашим сервисом.",
                            reply_markup=Extend_kb(True)
                            )
                        checked_users += 1
                        await asyncio.sleep(0.2)

                    if checked_users == 0:
                        logger.info("Не найдено истекающих подписок через 3 дня.")
                    else:
                        logger.info(f"Истекающие подписки {checked_users} юзеров успешно обработаны")
                except Exception as e:
                    logger.error(f"Ошибка при проверке подписок, заканчивающихся через 3 дня: {e}")
                    print(end_log)
                    
                # истеченные обычные подписки
                try:
                    checked_users = 0
                    expired_subscriptions = await sub_dao.get_all(
                        Subscription.end_date <= currently_msk())

                    for subscription in expired_subscriptions:
                        user_id = subscription.user_id
                        vless_link_id = subscription.vless_link_id
                        
                        user_dao = BaseDAO(User, db_session)
                        logger.info(f"У юзера {user_id} закончилась подписка.")

                        user_info = await user_dao.get_one(User.user_id == user_id)
                        user_name = user_info.user_name if user_info and user_info.user_name else "без username"

                        link = f"tg://user?id={user_id}"
                        await bot.send_message(
                            chat_id=admin_id,
                            text=f'У пользователя {markdown.hlink(str(user_id), link)} (@{user_name}) закончилась подписка.',
                            )

                        # Удаляем подписку (FK SET NULL автоматически обнулит vless_link_id)
                        await sub_dao.delete(Subscription.user_id == user_id)                
                        logger.info(f'Истекшая подписка {user_id} была удалена.')

                        # Удаляем ключ из базы
                        if vless_link_id:
                            vless_dao = BaseDAO(VlessLinks, db_session)
                            await vless_dao.delete(VlessLinks.id == vless_link_id)
                            logger.info(f'VLESS ключ (id: {vless_link_id}) пользователя {user_id} удален из базы')

                        await bot.send_message(
                            chat_id=user_id,
                            text=
                                f"⛓️‍💥 Ваша подписка истекла!\n"
                                f"Пожалуйста, продлите её, чтобы снова пользоваться {BotParams.name_project} VPN.",
                            reply_markup=Extend_kb(False)
                            )
                        checked_users += 1
                        await asyncio.sleep(0.2)

                    if checked_users == 0:
                        logger.info("Не найдено истекших подписок.")
                    else:
                        logger.info(f"Истекшие подписки {checked_users} юзеров успешно обработаны")
                    print(end_log)
                except Exception as e:
                    logger.error(f"Ошибка при проверке истекших подписок: {e}")
                    print(end_log)
                
                try:
                    checked_trial_users = 0
                    user_dao = BaseDAO(User, db_session)
                    expired_trial_subscriptions = await trial_dao.get_all(
                        (TrialSubscription.end_date <= currently_msk()) & (TrialSubscription.end_date.isnot(None)))

                    for trial_subscription in expired_trial_subscriptions:
                        user_id = trial_subscription.user_id
                        vless_link_id = trial_subscription.vless_link_id
                        
                        logger.info(f"У юзера {user_id} закончилась пробная подписка.")

                        user_info = await user_dao.get_one(User.user_id == user_id)
                        user_name = user_info.user_name if user_info and user_info.user_name else "без username"

                        link = f"tg://user?id={user_id}"
                        await bot.send_message(
                            chat_id=admin_id,
                            text=f'У пользователя {markdown.hlink(str(user_id), link)} (@{user_name}) закончилась пробная подписка.',
                            )

                        # Обнуляем триальную подписку (FK SET NULL автоматически обнулит vless_link_id)
                        await trial_dao.update(
                            TrialSubscription.user_id == user_id,
                            {
                                "start_date": None,
                                "end_date": None,
                                "trial_used": True,
                                "vless_link_id": None
                            }
                        )
                        logger.info(f'Истекшая пробная подписка {user_id} была обнулена, trial_used = True.')

                        # Удаляем ключ из базы
                        if vless_link_id:
                            vless_dao = BaseDAO(VlessLinks, db_session)
                            await vless_dao.delete(VlessLinks.id == vless_link_id)
                            logger.info(f'VLESS ключ (id: {vless_link_id}) из триальной подписки пользователя {user_id} удален из базы')

                        await bot.send_message(
                            chat_id=user_id,
                            text=
                                f"⛓️‍💥 Ваша пробная подписка истекла!\n"
                                f"Приобретите полную подписку, чтобы продолжить пользоваться {BotParams.name_project} VPN.",
                            reply_markup=Extend_kb(False)
                            )
                        checked_trial_users += 1
                        await asyncio.sleep(0.2)

                    if checked_trial_users == 0:
                        logger.info("Не найдено истекших пробных подписок.")
                    else:
                        logger.info(f"Истекшие пробные подписки {checked_trial_users} юзеров успешно обработаны")
                    print(end_log)
                except Exception as e:
                    logger.error(f"Ошибка при проверке истекших пробных подписок: {e}")
                    print(end_log)
        finally:
            await bot.session.close()
    
    asyncio.run(_async())

