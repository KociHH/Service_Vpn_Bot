from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from settings import BotParams
from keyboards.reply_keyboard.buttons_names import MainButtons, NewsletterButtons, PaymentsUsers, OtherEWhere

def admin_kb() -> ReplyKeyboardMarkup:
    admin_ids = BotParams.admin_ids_str
    print(f"Admin_id: {admin_ids}")

    for admin_id in admin_ids:
        if admin_id:
            builder = ReplyKeyboardBuilder()
            builder.button(text='💎 Админ панель')
            return builder.as_markup(resize_keyboard=True)

# create r.button
def main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=MainButtons.newsletter)
    builder.button(text=MainButtons.load_files)
    builder.button(text=MainButtons.check_images)
    builder.button(text=MainButtons.info_payments)
    builder.adjust(2, 1)

    return builder.as_markup(resize_keyboard=True)

def yes_no() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text='Да')
    builder.button(text='Нет')
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def exit_() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(
        text=OtherEWhere.back
    )
    return builder.as_markup(resize_keyboard=True)

def yes_no_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text='Да')
    builder.button(text=NewsletterButtons.change_message)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def payments_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=PaymentsUsers.user_payments)
    builder.button(text=PaymentsUsers.all_payments)
    builder.button(text=OtherEWhere.back)
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

def change_content_send_bt() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=PaymentsUsers.user_payments)
    builder.button(text=PaymentsUsers.all_payments)
    builder.button(text=OtherEWhere.back)
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)