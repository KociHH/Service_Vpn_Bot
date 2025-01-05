from typing import Union

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.testing.plugin.plugin_base import logging

from bd_api.middle import logger


# function checking email domen
async def check_email(email: str, message: Message | None = None):
    try:
        v = validate_email(email)
        if v:
            print(f"Email '{email}' is valid and its domain exists.")
        else:
            print(f"Email '{email}' is valid, but its domain does not exist.")
    except EmailNotValidError as e:
        if message:
            await message.answer(f"❌ Этот email не валидный, попробуйте еще раз.")
        logger.error(f'Ошибка при обработке email пользователя {message.from_user.full_name}, {email}, ошибка: {e}')


# Saved data for callback and for message
async def process_callback_data(call_message: Union[CallbackQuery, Message], state: FSMContext):
    if isinstance(call_message.data, str):
        try:
            callback_data = call_message.data
            callback_dict = {k: int(v) if k == 'month' else v for k, v in (item.split(':') for item in callback_data.split(','))}

            logger.info(f'Пользователь с email {callback_dict}')
            await state.update_data(action=callback_dict)
        except Exception as e:
            logger.error(f"Ошибка обработки callback_data: {call_message.data}, {e}")
    else:
        logger.error(f"Не удалось обработать callback_data: {call_message.data}")
