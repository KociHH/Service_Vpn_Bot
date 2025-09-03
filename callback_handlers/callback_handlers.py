import traceback
from typing import Optional, Union
from aiogram import F
from aiogram import Router
from aiogram.enums import ChatAction
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from db.middlewares.middle import logger
from db.tables import User, Subscription, PaymentHistory
from keyboards.inline_keyboard.main_inline_keyboard import Main, Main_menu, Month_kb, return_kb_support, \
    Month, info2, info, info3, info_price_249, info_price_579, info_price_979
from keyboards.inline_keyboard.pay_inline_keyboard import CashMultiBt, CashMenu
from keyboards.reply_keyboard.state_reply import build_net_keyboard
from settings import DEFAULT_EMAIL, BotParams
from typing import Any
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from utils.other import url_support

router = Router()

text_answer_one = markdown.text(
    f'🗝VPN на {info.month} месяц\n\n'
    f'📄Цена: {info.price} ₽\n\n'
    f'👤Кол-во устройств: ∞\n\n'
    '⚙️Всë необходимое будет предоставлено после приобретения', sep='\n')

text_answer_two = markdown.text(
    f'🗝VPN на {info2.month} месяцев\n\n'
    f'📄Цена: {info2.price} ₽\n\n'
    f'👤Кол-во устройств: ∞\n\n'
    '⚙️Всë необходимое будет предоставлено после приобретения', sep='\n')

text_answer_tree = markdown.text(
    f'🗝VPN на {info3.month} месяцев\n\n'
    f'📄Цена: {info3.price} ₽\n\n'
    f'👤Кол-во устройств: ∞\n\n'
    '⚙️Всë необходимое будет предоставлено после приобретения', sep='\n')


async def handle_month_subscription(call: CallbackQuery, data):
    if data == Month.One_month:
        callback_data_month = CashMenu.MOVEMENT_OPLATA
        text = text_answer_one
    elif data == Month.Two_month:
        callback_data_month = CashMenu.MOVEMENT_OPLATA_TWO
        text = text_answer_two
    elif data == Month.Tree_month:
        callback_data_month = CashMenu.MOVEMENT_OPLATA_TREE
        text = text_answer_tree
    else:
        return
    
    await call.message.answer(
        text=text,
        reply_markup=CashMultiBt(callback_data_month)
    )


@router.callback_query(F.data.in_((Month.One_month, Month.Two_month, Month.Tree_month)))
async def month_processing(call: CallbackQuery, db_session: AsyncSession):
    user_id = call.from_user.id
    try:
        user_dao = BaseDAO(User, db_session)
        existing_user = await user_dao.get_one(User.user_id == user_id)

        if existing_user:
            await call.answer()
            await handle_month_subscription(call, call.data)
        else:
            return

    except Exception as e:
        logger.error(f"Ошибка в функции : {e}")
        await call.answer(f"⚙️ Произошла ошибка, скоро исправим", show_alert=True)


@router.callback_query(F.data == Main.MAIN)
async def start(call: CallbackQuery):

    text = markdown.text(
        f"Здравствуйте, {call.from_user.full_name}!\n\n"
        f"🗝️ Познакомьтесь с {BotParams.name_project} VPN:\n",
        "🌑 I Скорость до 10 Гбит/с\n",
        "👁‍🗨 II Непрерывная маскировка IP-адреса и безопасность\n",
        "💻 III Современный интерфейс\n",
        "💳 Оплата картами РФ и СБП",
        sep='\n',
    )
    await call.message.edit_text(text, reply_markup=Main_menu())


@router.callback_query(F.data == Main.purchase)
async def purchase(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        text=markdown.text(
            f'⏳VPN {info_price_249.month} месяц\n'
            'Описание:\n'
            f'Цена: {info_price_249.price}\n'
            f'Кол-во устройств: ∞\n\n'

            f'⛓️VPN {info_price_579.month} месяца\n'
            'Описание:\n'
            f'Цена: {info_price_579.price}\n'
            f'Кол-во устройств: ∞\n\n'

            f'🌪️VPN {info_price_979.month} месяцев\n'
            'Описание:\n'
            f'Цена: {info_price_979.price}\n'
            f'Кол-во устройств: ∞''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀',
            sep='\n'
        ),
        reply_markup=Month_kb()
    )


@router.callback_query(F.data == Main.advantages)
async def purchase_advantages(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        text=markdown.text(
            f"🗝️ {BotParams.name_project} VPN:\n\n"
            "🌑 I Cкорость до 10 Гбит/с\n\n"
            "👁‍🗨 II Непрерывная маскировка IP-адреса и безопасность от отслеживания, перехватов и т. д.\n",
            f"💻 III Современность {BotParams.name_project} VPN дает WireGuard, защита и интерфейс",
            sep='\n'),
        reply_markup=return_kb_support(),
    )


@router.callback_query(F.data == Main.Support)
async def purchase_Support(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        text=markdown.text(
            f'💬 Если у вас возникли вопросы, смело обращайтесь в поддержку {markdown.hlink(title=BotParams.name_project, url=url_support)}\n\n',
        ),
        reply_markup=return_kb_support())
