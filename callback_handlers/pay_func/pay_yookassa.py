import logging
import uuid
import pytz
from typing import Union
import yookassa
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Configuration, Payment
from aiogram import Router
from utils.other import yookassa_bool
import settings
from db.middlewares.middle import logger
from db.tables import subscriber, Subscription


def configure_yookassa(true_module):
    if true_module:
        Configuration.secret_key = settings.YookassaToken.Api_key_test
        Configuration.account_id = settings.YookassaToken.Api_id_test
    else:
        Configuration.account_id = settings.YookassaToken.Api_id
        Configuration.secret_key = settings.YookassaToken.Api_key


configure_yookassa(yookassa_bool)
router = Router(name=__name__)


def create_oplata(amount, chat_id, month, description):
    id_key = str(uuid.uuid4())
    payment = Payment.create({

        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/vpnshadebot"
        },
        "capture": True,
        "metadata": {
            "chat_id": chat_id
        },
        "description": description,
        "receipt": {
            "customer": {
                "email": "example@example.com"
            },
            "items": [
                {
                    "description": description,
                    "quantity": 1.0,
                    "amount": {
                        "value": amount,
                        "currency": "RUB"
                    },
                    "vat_code": 6
                }
            ]
        },
        "test": False
    }, id_key)
    return payment.confirmation.confirmation_url, payment.id


async def check(payment_id, call: CallbackQuery, month: int, date: int, db_session: AsyncSession):
    user_id = call.from_user.id
    try:

        payment = yookassa.Payment.find_one(payment_id)

        if payment is None:
            logger.error(f'Платёж с ID {payment_id} не найден.')
            return False

        logger.info(f'Payment status: {payment.status}')

        if payment.status != "succeeded":
            return False

        subscriber_obj = subscriber(
            user_id=user_id,
            month=month,
            db_session=db_session
        )
        await subscriber_obj.date_Subscribers()
        logger.info(f"Успешно обновил подписку для пользователя: {user_id}.")
        return payment.metadata

    except Exception as e:
        logger.warning(f'Ошибка при проверке платежа: {e}, Платёж ID: {payment_id}')
        return False