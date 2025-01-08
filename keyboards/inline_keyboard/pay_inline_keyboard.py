from enum import IntEnum, auto
from typing import Union

from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bd_api.middle import logger
from bd_api.middlewares.sa_tables import User
from callback_handlers.pay_func.pay_yookassa import create_oplata
# create_oplata_two, create_oplata_tree
from keyboards.inline_keyboard.main_inline_keyboard import MainCD, Main, info, info3, info2
from settings import DEFAULT_EMAIL

router = Router()


class CashMenu(IntEnum):
    MOVE_OPLATA = auto()
    MOVE_OPLATA_TWO = auto()
    MOVE_OPLATA_TREE = auto()
    MOVEMENT_OPLATA = auto()
    MOVEMENT_OPLATA_TWO = auto()
    MOVEMENT_OPLATA_TREE = auto()


class CashCK(CallbackData, prefix='cash'):
    action: CashMenu


async def get_all_emails(user_id: int, db_session: AsyncSession):
    result = await db_session.execute(select(User.email).where(User.user_id == user_id))
    email = result.scalars().first()
    print(email)
    return email


class info_month():
    def __init__(
            self,
            price: float,
            month: int,
            description: str,
            callback_data: CashCK,
            MOVEMENT_OPLATA: CashMenu.MOVEMENT_OPLATA,
            MOVEMENT_OPLATA_TWO: CashMenu.MOVEMENT_OPLATA_TWO,
            MOVEMENT_OPLATA_TREE: CashMenu.MOVEMENT_OPLATA_TREE = None
    ) -> None:

        self.price = price
        self.month = month
        self.description = description
        self.callback_data = callback_data
        self.MOVEMENT_OPLATA = MOVEMENT_OPLATA
        self.MOVEMENT_OPLATA_TWO = MOVEMENT_OPLATA_TWO
        self.MOVEMENT_OPLATA_TREE = MOVEMENT_OPLATA_TREE

    def change_month_price(self):
        if self.callback_data.action == self.MOVEMENT_OPLATA:
            self.description = info.description
            self.month = info.month
            self.price = info.price
        elif self.callback_data.action == self.MOVEMENT_OPLATA_TWO:
            self.description = info2.description
            self.month = info2.month
            self.price = info2.price
        elif self.callback_data.action == self.MOVEMENT_OPLATA_TREE:
            self.description = info3.description
            self.month = info3.month
            self.price = info3.price
        return self.price, self.month, self.description

    async def oplatas(self, message: Message, db_session: AsyncSession) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        email = await get_all_emails(message.chat.id, db_session=db_session)
        payment_url, payment_id = create_oplata(self.price, message.chat.id, email, self.month, self.description)

        if not payment_url or not payment_id:
            logger.error(f'Ошибка создания платежа: {payment_url}, {payment_id}')
            raise ValueError('Ошибка создания платежа')

        builder.button(
            text='💳 Приобрести VPN',
            url=payment_url
        )
        builder.button(
            text='🔄 Поверка оплаты',
            callback_data=f'test_check_{payment_id}'
        )
        builder.adjust(1)
        return builder.as_markup()



def Cash_Bt() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'Перейти к оплате',
        callback_data=CashCK(action=CashMenu.MOVEMENT_OPLATA).pack()
    )
    builder.button(
        text='⬅️ Назад',
        callback_data=MainCD(action=Main.purchase).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def Cash_Bt_Two() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'Перейти к оплате',
        callback_data=CashCK(action=CashMenu.MOVEMENT_OPLATA_TWO).pack()
    )
    builder.button(
        text='⬅️ Назад',
        callback_data=MainCD(action=Main.purchase).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def Cash_Bt_Tree() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'Перейти к оплате',
        callback_data=CashCK(action=CashMenu.MOVEMENT_OPLATA_TREE).pack()
    )
    builder.button(
        text='⬅️ Назад',
        callback_data=MainCD(action=Main.purchase).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()
