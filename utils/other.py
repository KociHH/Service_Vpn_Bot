from aiogram.utils import markdown
import logging

from aiogram.utils.deep_linking import create_deep_link
from db.tables import PaymentHistory
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from aiogram.types import CallbackQuery, Message
from keyboards.inline_keyboard.common import slide_kb

from settings import BotParams

logger = logging.getLogger(__name__)

class OperationNames:
    uids_payments_link = "uidPaymentsLinks"
    payments_user = "paymentsUser"
    all_payments_users = "allPaymentsUsers"

async def create_slide_payments_bt(
    db_session: AsyncSession,
    user_id: int | str | None,
    message: Message | CallbackQuery,
    slide: int,
    operation_name: str,
    slide_from: int | None = None
    ): 
    if isinstance(message, CallbackQuery):
        message_obj = message.message
    else:
        message_obj = message

    if operation_name in [OperationNames.payments_user, OperationNames.all_payments_users]:
        max_content_rows_slide = 10
    elif operation_name == OperationNames.uids_payments_link:
        max_content_rows_slide = 15

    start_index = (slide - 1) * max_content_rows_slide
    end_index = start_index + max_content_rows_slide

    if operation_name == OperationNames.uids_payments_link:
        pay_dao = BaseDAO(PaymentHistory, db_session)
        all_payments_users = await pay_dao.get_all_column_values(PaymentHistory.user_id)

        if not all_payments_users:
            logger.error(f"Ошибочно нет юзеров")
            return

        all_payments_users = list(set(all_payments_users))
        total_content = len(all_payments_users)

        current_all_users = all_payments_users[start_index:end_index]

        result = ''
        for uid in current_all_users:
            link = create_deep_link(username=BotParams.username_bot, payload=f"{OperationNames.payments_user}_{uid}", link_type="start")
            result += f"\n{markdown.hlink(str(uid), url=link)}"
        text = result

    elif operation_name == OperationNames.payments_user and user_id:
        pay_dao = BaseDAO(PaymentHistory, db_session)
        all_payments = await pay_dao.get_all_column_values(
            (PaymentHistory.date_paid, PaymentHistory.payment_amount),
            PaymentHistory.user_id == user_id,
        )
        
        if not all_payments:
            logger.error(f"Ошибочно нет транзакций юзера {user_id}")
            return

        all_payments.sort(key=lambda payment: payment[0], reverse=True)
        total_content = len(all_payments)

        current_slide_payments = all_payments[start_index:end_index]

        result_text = ''
        for pay in current_slide_payments:
            result_text += f"\n{pay[1]}₽    :    {markdown.hcode(f'{pay[0]}')}" 
        text = f"{markdown.hcode(f'{user_id}')}\n{markdown.hbold("Сумма")}    :    {markdown.hbold("Дата оплаты (от новых к старым)")}\n{result_text}"

    elif operation_name == OperationNames.all_payments_users:
        pay_dao = BaseDAO(PaymentHistory, db_session)
        all_payments_users = await pay_dao.get_all()

        if not all_payments_users:
            logger.error(f"Ошибочно нет юзеров")
            return

        total_content = len(all_payments_users)

        all_payments_users.sort(key=lambda obj: obj.date_paid, reverse=True)
        current_all_users = all_payments_users[start_index:end_index]
        
        result = ""
        for obj in current_all_users:
            result += f"\n{obj.user_id}   :    {markdown.hcode(obj.date_paid)}    :    {obj.payment_amount}₽"

        text = f"{markdown.hbold('id')}    :    {markdown.hbold('Дата оплаты (от новых к старым)')}    :    {markdown.hbold('Сумма')}\n{result}"

    else:
        logger.error(f"Неверное operation_name: {operation_name}")
        return

    if not text:
        logger.error("В переменную text ничего не было добавленo в функции create_slide_bt.")
        return

    total_slides = (total_content + max_content_rows_slide - 1) // max_content_rows_slide
    slide = max(1, min(slide, total_slides))

    empty_button_left = (slide == 1)
    empty_button_right = (slide == total_slides)
    
    text = f"{text}\n\nСтр. {slide} из {total_slides}"
    message_result = message_obj.answer
    if slide > 1 or any([slide_from, slide_from == 1]):
        message_result = message_obj.edit_text

    await message_result(
        text=text,
        reply_markup=slide_kb(
            slide,
            operation_name,
            user_id,
            empty_button_left,
            empty_button_right
        )
    )
    return


def samples_(texts: list[str]):
    t = '—'
    result = []
    for text in texts:
        text = str(text).strip()
        line = t * (len(text) // 2)
        result.append(f'{text}\n{line}')
    return "\n\n".join(result)