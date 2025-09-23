from datetime import datetime
from enum import StrEnum, auto
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils import markdown
from settings import BotParams

class Month:
    One_month = "One_month"
    Two_month = "Two_month"
    Tree_month = "Tree_month"

class Main:
    extend = "extend"
    purchase = "purchase"
    advantages = "advantages"
    Support = "Support"
    MAIN = "MAIN"
    gift_free_subscription = "gift_free_subscription"

class Other:
    slide = "slide_"

class Price_and_us_and:
    def __init__(self, price: float | str , month: int, us: int | str = '∞', description: str | None = None):
        self.description = description
        self.price = price
        self.us = us
        self.month = month

info = Price_and_us_and(price=390.00, month=1, description=f'{BotParams.name_project} VPN на 1 месяц')
info2 = Price_and_us_and(price=990.00, month=3, description=f'{BotParams.name_project} VPN на 3 месяца')
info3 = Price_and_us_and(price=1690.00, month=6, description=f'{BotParams.name_project} VPN на 6 месяцев')

info_price_249 = Price_and_us_and('390₽ (-11%)', 1)
info_price_579 = Price_and_us_and('990₽ (-23%)', 3)
info_price_979 = Price_and_us_and('1690₽ (-35%)', 6)

def Main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text='Приобрести VPN',
        callback_data=Main.purchase),
    builder.button(
        text='Наши преимущества',
        callback_data=Main.advantages)
    builder.button(
        text='Поддержка',
        callback_data=Main.Support)
    builder.button(
        text='Пробный доступ',
        callback_data=Main.gift_free_subscription)
    builder.button(
        text='Наш телеграм чат',
        url=BotParams.username_channel)
    
    builder.adjust(1)
    return builder.as_markup()


def Month_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text='1 месяц',
        callback_data=Month.One_month)
    builder.button(
        text='3 месяца',
        callback_data=Month.Two_month)
    builder.button(
        text='6 месяцев',
        callback_data=Month.Tree_month)
    builder.button(
        text='⬅️ Назад',
        callback_data=Main.MAIN,)
    
    builder.adjust(1)
    return builder.as_markup()


def return_kb_support() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text='⬅️ Назад',
        callback_data=Main.MAIN)
    return builder.as_markup()


def Extend_kb(answer: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="➕ Продлить",
        callback_data=Main.extend if answer else Main.purchase
    )
    return builder.as_markup()


def slide_kb(
    count: int, 
    operation_name: str, 
    user_id: int | str | None,
    empty_button_left: bool = False,
    empty_button_right: bool = False
    ) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if user_id and user_id != None:
        user_id = f'{user_id}'
    else:
        user_id = 'None'

    left_data = f"{Other.slide}_{operation_name}_{user_id}_{count - 1}"
    text_bt_left = f"{count - 1} ◀️"
    if empty_button_left:
        text_bt_left = "⠀"
        left_data = "empty_button"

    right_data = f"{Other.slide}_{operation_name}_{user_id}_{count + 1}"
    text_bt_right = f"{count + 1} ▶️"
    if empty_button_right:
        text_bt_right = "⠀"
        right_data = "empty_button"

    builder.button(
        text=text_bt_left,
        callback_data=left_data
    )
    builder.button(
        text=text_bt_right,
        callback_data=right_data,
    )
    builder.adjust(2)
    return builder.as_markup()