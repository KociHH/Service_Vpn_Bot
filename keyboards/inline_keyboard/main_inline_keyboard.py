from datetime import datetime
from enum import IntEnum, auto
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils import markdown
from settings import BotParams

class Month(IntEnum):
    One_month = "One_month"
    Two_month = "Two_month"
    Tree_month = "Tree_month = auto()"

class MonthCD(CallbackData, prefix="month"):
    action: Month

class Main(IntEnum):
    purchase = "purchase"
    advantages = "advantages"
    Support = "Support"
    Telegram = "Telegram"
    MAIN = "MAIN"


class Price_and_us_and:
    def __init__(self, price: float | str , month: int, us: int | str = '∞', description: str | None = None):
        self.description = description
        self.price = price
        self.us = us
        self.month = month

info = Price_and_us_and(price=249.00, month=1, description='Shade VPN на 1 месяц')
info2 = Price_and_us_and(price=579.00, month=3, description='Shade VPN на 3 месяца')
info3 = Price_and_us_and(price=979.00, month=6, description='Shade VPN на 6 месяцев')

info_price_249 = Price_and_us_and('249₽ (-11%)', 1)
info_price_579 = Price_and_us_and('579₽ (-23%)', 3)
info_price_979 = Price_and_us_and('979₽ (-35%)', 6)

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
        text='Наш телеграмм канал',
        url=BotParams.username_channel,
        callback_data=Main.Telegram)
    
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


def Return_kb_active() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Наш телеграмм канал',
        url=BotParams.username_channel,
        callback_data=Main.Telegram)
    return builder.as_markup()
