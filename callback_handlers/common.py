from aiogram import F, Bot
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils import markdown
from db.middlewares.middle import logger
from db.tables import PaymentHistory, User
from keyboards.inline_keyboard.common import Main, Main_menu, Month_kb, return_kb_support, \
    Month, info2, info, info3, info_price_249, info_price_579, info_price_979, Other
from keyboards.inline_keyboard.pay import CashMultiBt, CashMenu
from settings import BotParams
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from utils.work import admin_id, url_support
from utils.other import create_slide_payments_bt, OperationNames
import logging
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

logger = logging.getLogger(__name__)
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
async def start_deep_link(call: CallbackQuery):

    text = markdown.text(
        f"{markdown.hbold(f'Здравствуйте, {call.from_user.full_name}!')}\n\n"
        f"{markdown.hbold(f'🗝️ Познакомьтесь с {BotParams.name_project} VPN:')}\n",
        "— Скорость до 10 Гбит/с",
        "— Непрерывная маскировка",
        "— Современный интерфейс\n",
        f"{markdown.hbold(f'💳 Оплата картами РФ и СБП')}",
        sep='\n',
    )
    await call.message.edit_text(text, reply_markup=Main_menu())


@router.callback_query(F.data.in_((Main.purchase, Main.extend)))
async def purchase(call: CallbackQuery):
    await call.answer()
    if call.data == Main.extend:
        message = call.message.answer
    else:
        message = call.message.edit_text

    await message(
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


@router.callback_query(F.data == Main.gift_free_subscription)
async def gift_free_subscription(call: CallbackQuery):
    user_id = call.from_user.id
    username = call.from_user.username
    await call.answer()
    await call.message.answer(
        text="Для подключения пробного периода, с вами свяжется наша поддержка, в течении пары минут."
    )

    link = f"tg://user?id={user_id}"
    await call.message.bot.send_message(
        chat_id=admin_id,
        text=f"{markdown.hlink(str(user_id), link)} (@{username}) хочет активировать пробный доступ",
    )


@router.callback_query(F.data.startswith(Other.slide))
async def slide_processing(call: CallbackQuery, db_session: AsyncSession):    
    try:
        data_args = call.data.split("_")
        operation_name = data_args[2]
        user_id = data_args[3]
        slide_count = int(data_args[4])
        print(f"call: {call.data} user_id:{user_id} operation_name: {operation_name} slide_count: {slide_count}")

        if user_id == 'None':
            user_id = None
        else:
            user_id = int(user_id)

        if not any([slide_count, operation_name]):
            logger.error(f"Нет числа слайда либо не получен operation_name: {data_args}")
            return

        await call.answer()
        await create_slide_payments_bt(
            db_session,
            user_id,
            call,
            slide_count,
            operation_name,
            slide_count
        )
    except Exception as e:
        logger.error(f"Ошибка в функции slide_processing: {e}")
        return

@router.callback_query(F.data == "empty_button")
async def empty_button(call: CallbackQuery):
    await call.answer("Empty button")