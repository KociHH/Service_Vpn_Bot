import logging
import uuid

import asyncio
from typing import Any

import yookassa
from aiogram import F, Dispatcher, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, LabeledPrice
from aiogram.utils import markdown
from aiogram.client.default import DefaultBotProperties
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Configuration, Payment
from aiogram import Router

import settings
from bd_api.middlewares.sa_tables import User


def configure_yookassa(true_module):
    if true_module:
        Configuration.secret_key = settings.YookassaToken.Api_key_test
        Configuration.account_id = settings.YookassaToken.Api_id_test
    else:
        Configuration.account_id = settings.YookassaToken.Api_id
        Configuration.secret_key = settings.YookassaToken.Api_key


configure_yookassa(False)
router = Router(name=__name__)


def create_oplata(amount, chat_id, email, month, description):
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
            "return_url": "https://t.me/vpnammobot"
        },
        "capture": True,
        "metadata": {
            "chat_id": chat_id
        },
        "description": description,
        "receipt": {
            "customer": {
                "email": email
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


def check(payment_id):
    payment = yookassa.Payment.find_one(payment_id)
    try:
        logging.info(f'Payment status: {payment.status}')
        if payment.status == "succeeded":
            print(payment.metadata)
            return payment.metadata
        else:
            return False
    except Exception as e:
        logging.warning(f'Ошибка при проверке платежа: {e}')