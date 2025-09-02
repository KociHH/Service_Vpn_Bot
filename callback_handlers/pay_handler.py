import logging
import asyncio
import os
from typing import Union
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils import markdown
from aiogram import Router
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from utils.other import url_support, currently_msk
from callback_handlers.pay_func.pay_yookassa import check
from keyboards.inline_keyboard.pay_inline_keyboard import CashCK, CashMenu, info_month
from keyboards.inline_keyboard.main_inline_keyboard import info, info3, info2, Main
from utils.load_image import ImageProcessing, admin_id
from db.middlewares.middle import async_session
from db.tables import Images, PaidSubscribers, images_dao, paid_dao

logger = logging.getLogger(__name__)
router = Router(name=__name__)
current_time = currently_msk.strftime(f"Дата: {markdown.hbold('%Y-%m-%d')}, Время: {markdown.hbold('%H:%M')}")
load_dotenv()

image_processing = ImageProcessing(async_session, images_dao)


@router.callback_query(CashCK.filter())
async def cash_ck(call: CallbackQuery, callback_data: CashCK, state: FSMContext):
    await call.message.bot.send_chat_action(
        chat_id=call.message.chat.id,
        action=ChatAction.TYPING
    )
    try:

        subscription = info_month(
            price=0.0, 
            month=0,
            description="",
            callback_data=callback_data,
            MOVEMENT_OPLATA=CashMenu.MOVEMENT_OPLATA,
            MOVEMENT_OPLATA_TWO=CashMenu.MOVEMENT_OPLATA_TWO,
            MOVEMENT_OPLATA_TREE=CashMenu.MOVEMENT_OPLATA_TREE
        )

        if callback_data.action in [
            CashMenu.MOVEMENT_OPLATA,
            CashMenu.MOVEMENT_OPLATA_TWO,
            CashMenu.MOVEMENT_OPLATA_TREE
        ]:

            price, month, description = subscription.change_month_price()
            markup = await subscription.oplatas(call.message)


            await call.answer()
            await call.message.answer(
                text=(
                    f'{markdown.hbold(description)}\n\n'
                    'Ваш счет для оплаты создан:'
                ),
                reply_markup=markup
            )

            await state.update_data(actions=callback_data.action, month=int(month), counting=int(0))

        else:
            await call.answer("Неизвестная команда.")

    except Exception as e:
        error_msg = f'Проблема при обработке оплаты: {e}'
        await call.message.answer(
            f"{error_msg}\n"
            "Пожалуйста, попробуйте позже."
        )

@router.callback_query(lambda i: i.data.startswith('test_check_'))
async def check_handler(call: Union[CallbackQuery, Message], state: FSMContext):
    user_id = call.from_user.id
    username = f"@{call.from_user.username}"

    data = await state.get_data()
    month = data.get("month")
    counting = data.get("counting", 0)

    if counting > 0:
        await call.answer(
            '✅ Вы уже совершили оплату, ожидайте ответ от администрации.\n')
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

        payment_parts = call.data.split('_')
        payment_id = payment_parts[2]
        payment_amount = float(payment_parts[3])
        check_ = await check(payment_id, message_callback=call, month=month, date=currently_msk.date())

        if not check_:
            await call.message.answer(
                '❗ Оплата не прошла ❗\n\n'
                'Если вы уверены, что совершили оплату, пожалуйста,'
                f'обратитесь в поддержку - {url_support}'
            )
            return

        paid_create = await paid_dao.create({
            "user_id": user_id,
            "payment_amount": payment_amount,
            "date_paid": currently_msk,
        })
        if not paid_create:
            logger.error(f"Не добавились данные об оплате в базу {paid_dao.model.__name__} юзера {user_id}")

        await call.message.answer("✅ Оплата прошла успешно!")
        

        counting += 1
        await state.update_data(counting=counting)
        name, id_img, sub = await image_processing.send_crcode(call, user_id)

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
                f'Фотки закончились напиши {username} если нет то,\n'
                f'его {markdown.hlink(f"{link}", f"tg://user?id={user_id}")}\n'
                f'Он оплатил на {markdown.hbold(month)} месяц(-а)'
            )
            return

        # await call.answer(f'Подписка продлена до: {markdown.hcode(end)}')
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
        await image_processing.delete_code(call, id_img)
    except Exception as e:
        logging.error(f'Ошибка при проверке оплаты: {e}')
        await call.answer(
            "❗ Произошла ошибка при проверке платежа.\n"
            "Пожалуйста, попробуйте позже или обратитесь в поддержку - @ammosupport\n"
        )
