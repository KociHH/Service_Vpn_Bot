from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from settings import BotParams
from keyboards.reply_keyboard.buttons_names import FilterPayments, MainButtons, MonthsNames, NewsletterButtons, PaymentsUsers, OtherEWhere
from utils.work import currently_msk

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
    builder.button(text=PaymentsUsers.filter_amount_date)
    builder.button(text=OtherEWhere.back)
    builder.adjust(2, 1, 1)
    return builder.as_markup(resize_keyboard=True)

def change_content_send_bt() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=NewsletterButtons.change_text)
    builder.button(text=NewsletterButtons.change_all)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def continue_bt() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=NewsletterButtons.continue_action)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def months_input_bt() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=MonthsNames.january)
    builder.button(text=MonthsNames.february)
    builder.button(text=MonthsNames.march)
    builder.button(text=MonthsNames.april)
    builder.button(text=MonthsNames.may)
    builder.button(text=MonthsNames.june)
    builder.button(text=MonthsNames.july)
    builder.button(text=MonthsNames.august)
    builder.button(text=MonthsNames.september)
    builder.button(text=MonthsNames.october)
    builder.button(text=MonthsNames.november)
    builder.button(text=MonthsNames.december)
    builder.button(text=OtherEWhere.back)
    builder.adjust(2, 2, 2, 2, 2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

def count_year_month_bt() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=FilterPayments.filter_year_month)
    builder.button(text=FilterPayments.back_to_filter_month)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def years_dinamic_bt(last_year: str | int | None = None) -> ReplyKeyboardMarkup:
    # max 2
    builder = ReplyKeyboardBuilder() 
    size = 1
    if last_year:
        builder.button(text=f"{currently_msk().year}")
        builder.button(text=f"{last_year}")
    else:
        builder.button(text=f"{currently_msk().year}")

    builder.adjust(size)    
    return builder.as_markup(resize_keyboard=True)
