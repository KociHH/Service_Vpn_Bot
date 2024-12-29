from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import settings

# it is not used
def admin_kb() -> ReplyKeyboardMarkup:
    admin_ids = settings.Admins()
    print(f"Admin_id: {admin_ids}")

    for admin_id in admin_ids:
        if admin_id:
            builder = ReplyKeyboardBuilder()
            builder.button(text='💎 Админ панель')
            return builder.as_markup(resize_keyboard=True)

# create r.button
def rassilka_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text='📢 Рассылка')

    return builder.as_markup(resize_keyboard=True)

# create r.button
def yes_no_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text='Да')
    builder.button(text='📝 Изменить текст')
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
