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
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils import markdown
from aiogram import Router
from dotenv import load_dotenv
from environs import Env
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

import settings
# from bd_api.middlewares.db_sql import info_month
from bd_api.middlewares.sa_tables import User, UserUpdater, Subscription, subscriber
from callback_handlers.callback_handlers import upsert_user, purchase
# from callback_handlers.pay_func.pay_yookassa import check_one, \
#     check_tree, check_two
from callback_handlers.pay_func.pay_yookassa import check
from keyboards.inline_keyboard.pay_inline_keyboard import CashCK, CashMenu, info_month

from keyboards.inline_keyboard.main_inline_keyboard import info, info3, info2, MainCD, Main
from utils.date_moscow import get_current_date
from utils.image_ import send_crcode, delete_code, admin_id

logger = logging.getLogger(__name__)
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
                    'Ваш счет для оплаты создан:'
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
async def check_handler(call: Union[CallbackQuery, Message], db_session: AsyncSession, state: FSMContext):
    user_id = call.from_user.id
    username = f"@{call.from_user.username}"

    data = await state.get_data()
    month = data.get("month")
    counting = data.get("count_payment", 0)

    if counting > 0:
        await call.message.answer(
            '✅ Вы уже совершили оплату, ожидайте ответ от администрации.\n'
            'Или обратитесь в поддержку - @ammosupport')
        return

    if month is None:
        await call.answer("❗ Ошибка: данные месяца неизвестны. Пвоторите попытку")
        return

    await call.message.bot.send_chat_action(
        chat_id=call.message.chat.id,
        action=ChatAction.TYPING
    )

    try:
        await call.answer()
        if not call.data.startswith("test_check_"):
            logging.error(f"Некорректные данные callback_data: {call.data}")
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
                'Если вы уверены, что совершили оплату, пожалуйста,'
                'обратитесь в нашу поддержку - @ammosupport'
            )
            return

        await call.message.answer("✅ Оплата прошла успешно!")
        await asyncio.sleep(0.5)
        name, id_img, sub = await send_crcode(call, db_session, user_id)

        if not sub:
            logger.error("Подписка не найдена.")
            return

        start = 0
        end = 0
        for start_unpack, end_unpack in sub:
            start, end = start_unpack, end_unpack

        if id_img and name == 'Неизвестно':
            link = 'Прямая ссылка'
            await call.message.bot.send_message(
                chat_id = admin_id,
                text=
                f'Ебать фотки закончились, чел оплатил а их нет напиши {username} если нет то,\n'
                f'его {markdown.hlink(f"{link}", f"tg://user?id={user_id}")}\n'
                f'Он оплатил на {markdown.hbold(month)} месяц(-а) в {get_current_date(True)}'
            )
            return

        await call.answer(f'Подписка продлена до: {markdown.hbold(end)}')
        await call.message.bot.send_message(
            chat_id=admin_id,
            text=
            f'Пользователь успешно оплатил ⤵️\n\n'
            f'{markdown.hbold("Данные")}:\n'
            f'username: {username}\n'
            f'user_id: {user_id}\n'
            f'id QR-кода: {name}\n\n'
            f"{markdown.hbold('Время')}:\n"
            f"Когда прошел платеж: {start}\n"
            f"Истекает: {end}\n"
        )
        logger.info(
            f'Пользователь успешно оплатил:\n\n'                  
            f'username: {username}\n'
            f'user_id: {user_id}\n'
            f'ID кода: {name}\n'       
            f"Время:\n"
            f"Время платежа: {start}\n"
            f"Кончается: {end}\n"
        )
        await delete_code(call, db_session, id_img)
    except Exception as e:
        logging.error(f'Ошибка при проверке оплаты: {e}')
        await call.answer(
            "❗ Произошла ошибка при проверке платежа.\n"
            "Пожалуйста, попробуйте позже или обратитесь в поддержку - @ammosupport\n"
        )


# @router.callback_query(F.data == 'get_file')
# async def giv_config(call: CallbackQuery, state: FSMContext, db_session: AsyncSession):
#     data_state = await state.get_data()
#
#     action_count = data_state.get('action_count', 0)
#     action_count += 1
#
#     if action_count > 1:
#         await call.answer('🥳 Вы уже оплатили, ожидайте ответа')
#         return
#
#     await state.update_data(action_count=action_count)
#
#     admin_id = os.getenv('ADMIN_ID')
#
#     button_support = InlineKeyboardButton(
#         text="🤝 Обратиться в поддержку",
#         callback_data='contact_support',
#         url='https://t.me/ammosupport'
#     )
#
#     button_return_month = InlineKeyboardButton(
#         text='↩ Вернуться в меню выбора месяца',
#         callback_data='return_month'
#     )
#
#     inline_kb = InlineKeyboardMarkup(inline_keyboard=[
#         [button_support],
#         [button_return_month]
#     ])
#
#
#     data = data_state.get("actions")
#     callb = {
#         CashMenu.MOVEMENT_OPLATA: "1 месяц",
#         CashMenu.MOVEMENT_OPLATA_TWO: "2 месяца",
#         CashMenu.MOVEMENT_OPLATA_TREE: "3 месяца",
#     }
#
#     if data in callb:
#         value = callb[data]
#         await call.answer()
#         user = await db_session.execute(select(User).where(User.user_id == call.message.chat.id))
#         result = user.scalar_one_or_none()
#
#         if result:
#             name_user = call.message.chat.full_name
#             user_name = call.message.chat.username
#
#             if not name_user or name_user.strip() == "":
#                 name_user = 'ссылка'
#
#             if user_name is None:
#                 clickable_user = markdown.hlink(f"{name_user}", f"tg://user?id={call.message.chat.id}")
#             else:
#                 clickable_user = f"@{user_name}"
#
#             await call.message.bot.send_message(
#                 chat_id=admin_id,
#                 text=f'Пользователь {clickable_user} запросил файл на {markdown.hbold(value)},\n'
#                 f'{current_time}'
#             )
#
#             await call.message.answer(
#                 'Ваш запрос отправлен!\n\n'
#                 '⌛ В ближайшее время администратор вам ответит.\n\n'
#                 '✨ Если вам срочно нужен файл, то обратитесь напрямую, нажав на кнопку ниже',
#                 reply_markup=inline_kb
#             )
#
#             logger.info(f'Пользователь {clickable_user} запросил файл на {value}')
#
#     else:
#         logging.error(f"Некорректные данные в состоянии: {data}")
#
#
# @router.callback_query(F.data == 'return_month')
# async def returned_month(call: CallbackQuery):
#     await purchase(call)