from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def build_net_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text='Пропустить')
    builder.adjust(1)
    return builder.as_markup(input_field_placeholder='your email', resize_keyboard=True)


