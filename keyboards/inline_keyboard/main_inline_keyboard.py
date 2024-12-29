from datetime import datetime
from enum import IntEnum, auto

import yookassa
from aiogram import F
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils import markdown

url = 'https://t.me/ammovpnchannel'



class Month(IntEnum):
    One_month = auto()
    Two_month = auto()
    Tree_month = auto()

class MonthCD(CallbackData, prefix="month"):
    action: Month


class Main(IntEnum):
    purchase = auto()
    advantages = auto()
    Support = auto()
    Telegram = auto()
    MAIN = auto()


class MainCD(CallbackData, prefix='main'):
    action: Main


class Price_and_us_and():
    def __init__(self, price: float, us: int, month: int, description: str = None):
        self.description = description
        self.price = price
        self.us = us
        self.month = month


info = Price_and_us_and(179.00, 1, 1, 'AMMO VPN на 1 месяц')
info2 = Price_and_us_and(329.00, 1, 2, 'AMMO VPN на 2 месяца')
info3 = Price_and_us_and(449.00, 1, 3, 'AMMO VPN на 3 месяца')



def Main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text='Приобрести VPN',
        callback_data=MainCD(action=Main.purchase)),
    builder.button(
        text='Наши преимущества',
        callback_data=MainCD(action=Main.advantages))
    builder.button(
        text='Поддержка',
        callback_data=MainCD(action=Main.Support))

    builder.button(
        text='Наш телеграмм канал',
        url=url,
        callback_data=MainCD(action=Main.Telegram)
    )
    builder.adjust(1)
    return builder.as_markup()


def Month_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text='1 месяц',
        callback_data=MonthCD(action=Month.One_month).pack())
    builder.button(
        text='2 месяца',
        callback_data=MonthCD(action=Month.Two_month).pack())
    builder.button(
        text='3 месяца',
        callback_data=MonthCD(action=Month.Tree_month).pack())
    builder.button(
        text='⬅️ Назад',
        callback_data=MainCD(action=Main.MAIN).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def return_kb_support() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text='⬅️ Назад',
        callback_data=MainCD(action=Main.MAIN).pack()
    )
    return builder.as_markup()


def Return_kb_active() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Наш телеграмм канал',
        url=url,
        callback_data=MainCD(action=Main.Telegram))
    return builder.as_markup()
