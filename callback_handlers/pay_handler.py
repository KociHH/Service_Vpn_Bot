import logging

import asyncio
import os
from datetime import datetime, timezone
from typing import Union

import pytz
from aiogram import F
from aiogram.client import bot
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import markdown
from aiogram import Router
from dotenv import load_dotenv
from environs import Env
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from bd_api.middle import logger
# from bd_api.middlewares.db_sql import info_month
from bd_api.middlewares.sa_tables import User, UserUpdater, Subscription, subscriber
from callback_handlers.callback_handlers import upsert_user, purchase
# from callback_handlers.pay_func.pay_yookassa import check_one, \
#     check_tree, check_two
from callback_handlers.pay_func.pay_yookassa import check
from keyboards.inline_keyboard.pay_inline_keyboard import CashCK, CashMenu, info_month

from keyboards.inline_keyboard.main_inline_keyboard import info, info3, info2, MainCD, Main
from utils.date_moscow import get_current_date

router = Router(name=__name__)
current_time = get_current_date(False)
load_dotenv()


@router.callback_query(CashCK.filter())
async def cash_ck(call: CallbackQuery, callback_data: CashCK, state: FSMContext, db_session: AsyncSession):
    await call.message.bot.send_chat_action(
        chat_id=call.message.chat.id,
        action=ChatAction.TYPING
    )
    try:
        # Создаем экземпляр класса info_month

        subscription = info_month(
            price=0.0,
            month=0,
            description="",
            callback_data=callback_data,
            MOVEMENT_OPLATA=CashMenu.MOVEMENT_OPLATA,
            MOVEMENT_OPLATA_TWO=CashMenu.MOVEMENT_OPLATA_TWO,
            MOVEMENT_OPLATA_TREE=CashMenu.MOVEMENT_OPLATA_TREE
        )

        # Проверяем, что action существует в CashMenu
        if callback_data.action in [
            CashMenu.MOVEMENT_OPLATA,
            CashMenu.MOVEMENT_OPLATA_TWO,
            CashMenu.MOVEMENT_OPLATA_TREE
        ]:

            price, month, description = subscription.change_month_price()
            markup = await subscription.oplatas(call.message, db_session)
            print(month)


            await call.answer()
            await call.message.answer(
                text=(
                    f'{markdown.hbold(description)}\n\n'
                    'Счет сформирован:'
                ),
                reply_markup=markup
            )

            await state.update_data(actions=callback_data.action, action_count=0,  count_payment=0, month=int(month))

        else:
            await call.answer("Неизвестная команда.")

    except Exception as e:
        error_msg = f'Проблема при обработке оплаты: {e}'
        await call.message.answer(
            f"{error_msg}\n"
            "Пожалуйста, попробуйте позже."
        )


@router.callback_query(lambda i: i.data.startswith('test_check_'))
async def check_handler(call: CallbackQuery, db_session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    month = data.get("month")
    counting = data.get("count_payment", 0)
    print(month, counting)

    if counting > 0:
        await call.answer('✅ Вы уже совершили оплату, ожидайте ответ от администрации.')
        return

    if month is None:
        await call.answer("❗ Ошибка: данные месяца неизвестны.")
        return

    await call.message.bot.send_chat_action(
        chat_id=call.message.chat.id,
        action=ChatAction.TYPING
    )

    try:
        await call.answer()


        if not call.data.startswith("test_check_"):
            logger.error(f"Некорректные данные callback_data: {call.data}")
            await call.answer(
                "❗ Произошла ошибка при проверке платежа.\n"
                "Пожалуйста, попробуйте позже или обратитесь в поддержку"
            )
            return

        payment_id = call.data[len("test_check_"):]
        check_ = await check(payment_id, db_session, message_callback=call, month=month, date=get_current_date(True))

        if not check_:
            await call.message.answer(
                '❗ Оплата не прошла ❗\n\n'
                'Если вы уверены, что оплатили заказ, пожалуйста, '
                'обратитесь в нашу поддержку - @ammosupport'
            )
            return

        button = InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(
                        text="Оповестить об оплате",
                        callback_data="get_file"
                    )
                ]]
            )

        await call.message.answer(
            markdown.text(
                "✅ Оплата прошла успешно!\n\n"
                "Чтобы получить файл с инструкцией, нажмите на кнопку ниже",
                sep="\n"
                ),
            reply_markup=button
        )

        logger.info(
                f"Current Date and Time (MSK): {current_time}\n"
                f"Current User's Login: {call.from_user.username}\n"
                f"Checking payment ID: {payment_id}\n"
                f"User ID: {call.from_user.id}"
        )
        counting += 1
        await state.update_data(count_payment=counting)

    except Exception as e:
        logger.error(f'Ошибка при проверке оплаты: {e}')
        await call.answer(
            "❗ Произошла ошибка при проверке платежа.\n"
            "Пожалуйста, попробуйте позже или обратитесь в поддержку - @ammosupport\n"
        )





@router.callback_query(F.data == 'get_file')
async def giv_config(call: CallbackQuery, state: FSMContext, db_session: AsyncSession):
    data_state = await state.get_data()

    action_count = data_state.get('action_count', 0)
    action_count += 1

    if action_count > 1:
        await call.answer('🥳 Вы уже оплатили, ожидайте ответа')
        return

    await state.update_data(action_count=action_count)

    admin_id = os.getenv('ADMIN_ID')

    button_support = InlineKeyboardButton(
        text="🤝 Обратиться в поддержку",
        callback_data='contact_support',
        url='https://t.me/ammosupport'
    )

    button_return_month = InlineKeyboardButton(
        text='↩ Вернуться в меню выбора месяца',
        callback_data='return_month'
    )

    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [button_support],
        [button_return_month]
    ])


    data = data_state.get("actions")
    callb = {
        CashMenu.MOVEMENT_OPLATA: "1 месяц",
        CashMenu.MOVEMENT_OPLATA_TWO: "2 месяца",
        CashMenu.MOVEMENT_OPLATA_TREE: "3 месяца",
    }

    if data in callb:
        value = callb[data]
        await call.answer()
        user = await db_session.execute(select(User).where(User.user_id == call.message.chat.id))
        result = user.scalar_one_or_none()

        if result:
            name_user = call.message.chat.full_name
            user_name = call.message.chat.username

            if not name_user or name_user.strip() == "":
                name_user = 'ссылка'

            if user_name is None:
                clickable_user = markdown.hlink(f"{name_user}", f"tg://user?id={call.message.chat.id}")
            else:
                clickable_user = f"@{user_name}"

            await call.message.bot.send_message(
                chat_id=admin_id,
                text=f'Пользователь {clickable_user} запросил файл на {markdown.hbold(value)},\n'
                f'{current_time}'
            )

            await call.message.answer(
                'Ваш запрос отправлен!\n\n'
                '⌛ В ближайшее время администратор вам ответит.\n\n'
                '✨ Если вам срочно нужен файл, то обратитесь напрямую, нажав на кнопку ниже',
                reply_markup=inline_kb
            )

            logger.info(f'Пользователь {clickable_user} запросил файл на {value}')

    else:
        logging.error(f"Некорректные данные в состоянии: {data}")


@router.callback_query(F.data == 'return_month')
async def returned_month(call: CallbackQuery):
    await purchase(call)