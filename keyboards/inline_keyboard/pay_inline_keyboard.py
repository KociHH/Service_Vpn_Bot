from aiogram import Router
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Any
from db.middlewares.middle import logger
from callback_handlers.pay_func.pay_yookassa import create_oplata
from keyboards.inline_keyboard.main_inline_keyboard import Main, info, info3, info2, Month


router = Router()

class CashMenu:
    MOVEMENT_OPLATA = "MOVEMENT_OPLATA"
    MOVEMENT_OPLATA_TWO = "MOVEMENT_OPLATA_TWO"
    MOVEMENT_OPLATA_TREE = "MOVEMENT_OPLATA_TREE"

class info_month:
    def __init__(
            self,
    ) -> None:

        self.price = 0
        self.month = 0
        self.description = ""

    def change_month_price(self, callback_data: Any):
        if callback_data == CashMenu.MOVEMENT_OPLATA:
            self.description = info.description
            self.month = info.month
            self.price = info.price
        elif callback_data == CashMenu.MOVEMENT_OPLATA_TWO:
            self.description = info2.description
            self.month = info2.month
            self.price = info2.price
        elif callback_data == CashMenu.MOVEMENT_OPLATA_TREE:
            self.description = info3.description
            self.month = info3.month
            self.price = info3.price
        return self.price, self.month, self.description

    async def oplatas(self, message: Message) -> InlineKeyboardMarkup:
        user_id = message.chat.id
        builder = InlineKeyboardBuilder()
        payment_url, payment_id = create_oplata(self.price, user_id, self.month, self.description)

        if not payment_url or not payment_id:
            logger.error(f'Ошибка создания платежа: {payment_url}, {payment_id}')
            raise ValueError('Ошибка создания платежа')

        builder.button(
            text='💳 Приобрести VPN',
            url=payment_url
        )
        builder.button(
            text='🔄 Поверка оплаты',
            callback_data=f'test_check_{payment_id}_{self.price}'
        )
        builder.adjust(1)
        return builder.as_markup()


def CashMultiBt(
        callback_data_cash: Any,
        ) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'Перейти к оплате',
        callback_data=callback_data_cash
    )
    builder.button(
        text='⬅️ Назад',
        callback_data=Main.purchase,
    )
    builder.adjust(1)
    return builder.as_markup()
