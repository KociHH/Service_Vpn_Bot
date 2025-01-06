import logging

import asyncio
from datetime import datetime, timezone
from typing import Union

from aiogram import F
from aiogram.client import bot
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import markdown
from aiogram import Router
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from bd_api.middle import logger
# from bd_api.middlewares.db_sql import info_month
from bd_api.middlewares.sa_tables import User, UserUpdater
from callback_handlers.callback_handlers import upsert_user, purchase
# from callback_handlers.pay_func.pay_yookassa import check_one, \
#     check_tree, check_two
from callback_handlers.pay_func.pay_yookassa import check
from keyboards.inline_keyboard.pay_inline_keyboard import CashCK, CashMenu, info_month

from keyboards.inline_keyboard.main_inline_keyboard import info, info3, info2, MainCD, Main

router = Router(name=__name__)



@router.callback_query(CashCK.filter())
async def cash_ck(call: CallbackQuery, callback_data: CashCK, state: FSMContext, db_session: AsyncSession):
    await call.message.bot.send_chat_action(
        chat_id=call.message.chat.id,
        action=ChatAction.TYPING
    )
    data = call.data
    print(data)
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

            # Отправляем сообщение с информацией о подписке
            await call.answer()
            await call.message.answer(
                text=(
                    f'{markdown.hbold(description)}\n\n'
                    'Счет сформирован:'
                ),
                reply_markup=markup
            )

            # Сохраняем данные в состоянии
            await state.update_data(actions=callback_data.action, action_count=0)

            logging.info(
                f"Данные сохранены в состоянии: "
                f"action={callback_data.action}, "
                f"price={price}, "
                f"month={month}, "
                f"description={description}"
            )
        else:
            await call.answer("Неизвестная команда.")

    except Exception as e:
        error_msg = f'Проблема при обработке оплаты: {e}'
        logging.exception(error_msg)
        await call.message.answer(
            "Произошла ошибка при формировании счета. "
            "Пожалуйста, попробуйте позже."
        )


@router.callback_query(lambda i: 'test_check_' in i.data)
async def check_handler(call: CallbackQuery, db_session: AsyncSession, state: FSMContext):
    await call.message.bot.send_chat_action(
        chat_id=call.message.chat.id,
        action=ChatAction.TYPING
    )

    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    try:
        await call.answer()

        # Проверка корректности callback_data
        if not call.data.startswith("test_check_"):
            logging.error(f"Некорректные данные callback_data: {call.data}")
            await call.answer(
                "❗ Произошла ошибка при проверке платежа.\n"
                "Пожалуйста, попробуйте позже или обратитесь в поддержку"
            )
            return

        # Извлечение payment_id
        payment_id = call.data[len("test_check_"):]


        # Проверка оплаты
        if asyncio.iscoroutinefunction(check):
            result = await check(payment_id)
        else:
            result = check(payment_id)

        if not result:
            await call.message.answer(
                '❗ Оплата не прошла ❗\n\n'
                'Если вы уверены, что оплатили заказ, пожалуйста, '
                'обратитесь в нашу поддержку - @ammosupport'
            )
            return

        # Оплата успешна
        await upsert_user(db_session=db_session, call_and_message=call, email=None)

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
        logging.info(
            f"Current Date and Time (UTC): {current_time}\n"
            f"Current User's Login: {call.from_user.username}\n"
            f"Checking payment ID: {payment_id}\n"
            f"User ID: {call.from_user.id}"
        )

    except Exception as e:
        logging.error(f'Ошибка при проверке оплаты: {e}')
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

    admin_id = 7090846284

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
                text=f'Пользователь {clickable_user} запросил файл на {markdown.hbold(value)}'
            )
            # await call.message.answer(f'Пользователь {clickable_user} запросил файл на {markdown.hbold(value)}')
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