from aiogram import F, Bot
from aiogram import Router
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram.utils import markdown
from db.middlewares.middle import logger
from db.tables import PaymentHistory, User, Subscription, VlessLinks, TrialSubscription
from keyboards.inline_keyboard.common import Main, Main_menu, Month_kb, return_kb_support, \
    Month, info2, info, info_price_249, info_price_579, Other
from keyboards.inline_keyboard.pay import CashMultiBt, CashMenu
from settings import BotParams
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from utils.work import admin_id, url_support
from utils.other import create_slide_payments_bt, OperationNames, main_photo
import logging
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from datetime import timedelta
from utils.work import currently_msk
import random
from utils.work import admin_id

logger = logging.getLogger(__name__)
router = Router()

text_answer_one = markdown.text(
    f'🗝VPN на {info.month} месяц\n\n'
    f'📄Цена: {info.price} ₽\n\n'
    f'👤Кол-во устройств: 3\n\n'
    '⚙️Всë необходимое будет предоставлено после приобретения', sep='\n')

text_answer_two = markdown.text(
    f'🗝VPN на {info2.month} месяцев\n\n'
    f'📄Цена: {info2.price} ₽\n\n'
    f'👤Кол-во устройств: 3\n\n'
    '⚙️Всë необходимое будет предоставлено после приобретения', sep='\n')


async def handle_month_subscription(call: CallbackQuery, data):
    if data == Month.One_month:
        callback_data_month = CashMenu.MOVEMENT_OPLATA
        text = text_answer_one
    elif data == Month.Two_month:
        callback_data_month = CashMenu.MOVEMENT_OPLATA_TWO
        text = text_answer_two
    else:
        return
    
    await call.message.answer(
        text=text,
        reply_markup=CashMultiBt(callback_data_month)
    )


@router.callback_query(F.data.in_((Month.One_month, Month.Two_month)))
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
async def start_deep_link(call: CallbackQuery, db_session: AsyncSession):
    user_id = call.from_user.id
    
    trial_dao = BaseDAO(TrialSubscription, db_session)
    trial_subscription = await trial_dao.get_one(TrialSubscription.user_id == user_id)
    
    show_trial = not (trial_subscription and trial_subscription.trial_used)

    text = markdown.text(
        f"{markdown.hbold('🔓 Познакомься с Shade VPN:')}\n\n"
    
        "— Скорость до 1 Гбит/с\n"
        "— No-Logs политика\n"
        "— Подписка до 3 устройств\n"
        "— Непрерывная маскировка\n"
        "— Современный интерфейс\n"
        "— Поддержка Android, IOS, Windows, MacOS, AndroidTV, Linux\n\n"
        
        "🔥 Подписывайся на наш канал по кибербезопасности!\n\n",
        
        "🎉 Держи бесплатную пробную подписку на Shade VPN на 3 дня абсолютно бесплатно!\n" if show_trial else "",
        sep=""
    )
    
    try:
        media = InputMediaPhoto(media=main_photo, caption=text)
        await call.message.edit_media(
            media=media,
            reply_markup=Main_menu(show_trial=show_trial)
        )
    except Exception as e:
        if "message is not modified" in str(e):
            await call.answer()
        else:
            raise


@router.callback_query(F.data.in_((Main.purchase, Main.extend)))
async def purchase(call: CallbackQuery):
    await call.answer()
    
    text = markdown.text(
        f'⏳VPN {info_price_249.month} месяц\n'
        'Описание:\n'
        f'Цена: {info_price_249.price}\n'
        f'Кол-во устройств: 3\n\n'

        f'⛓️VPN {info_price_579.month} месяца\n'
        'Описание:\n'
        f'Цена: {info_price_579.price}\n'
        f'Кол-во устройств: 3\n\n',

        sep='\n'
    )
    
    if call.data == Main.extend:
        await call.message.answer_photo(
            photo=main_photo,
            caption=text,
            reply_markup=Month_kb()
        )
    else:
        try:
            media = InputMediaPhoto(media=main_photo, caption=text)
            await call.message.edit_media(
                media=media,
                reply_markup=Month_kb()
            )

        except Exception as e:
            if "message is not modified" in str(e):
                await call.answer()
            else:
                raise


@router.callback_query(F.data == Main.advantages)
async def purchase_advantages(call: CallbackQuery):
    await call.answer()
    
    text = markdown.text(
        f"🗝️ {BotParams.name_project} VPN:\n\n"
        "🌑 I Cкорость до 10 Гбит/с\n\n"
        "👁‍🗨 II Непрерывная маскировка IP-адреса и безопасность от отслеживания, перехватов и т. д.\n",
        f"💻 III Современность {BotParams.name_project} VPN дает WireGuard, защита и интерфейс",
        sep='\n'
    )
    
    try:
        media = InputMediaPhoto(media=main_photo, caption=text)
        await call.message.edit_media(
            media=media,
            reply_markup=return_kb_support()
        )
        
    except Exception as e:
        if "message is not modified" in str(e):
            pass
        else:
            raise


@router.callback_query(F.data == Main.Support)
async def purchase_Support(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        text=markdown.text(
            f'💬 Если у вас возникли вопросы, смело обращайтесь в поддержку {markdown.hlink(title=BotParams.name_project, url=url_support)}\n\n',
        ),
        reply_markup=return_kb_support())


@router.callback_query(F.data == Main.gift_free_subscription)
async def gift_free_subscription(call: CallbackQuery, db_session: AsyncSession):
    user_id = call.from_user.id
    username = call.from_user.username
    await call.answer()
    
    trial_dao = BaseDAO(TrialSubscription, db_session)
    trial_subscription = await trial_dao.get_one(TrialSubscription.user_id == user_id)
    
    if trial_subscription and trial_subscription.trial_used:
        await call.message.answer(
            text="❌ Вы уже использовали пробный период ранее."
        )
        return
    
    vless_dao = BaseDAO(VlessLinks, db_session)
    # Получаем свободные ссылки (не используемые)
    all_links = await vless_dao.get_all(VlessLinks.using == False)
    
    if not all_links:
        await call.message.answer(
            text="⚠️ К сожалению, в данный момент нет доступных ссылок. Обратитесь в поддержку."
        )
        return
    
    selected_link = random.choice(all_links)
    vless_link = selected_link.src
    link_id = selected_link.id
    
    current_date = currently_msk()
    trial_end_date = current_date + timedelta(days=3)
    
    # Помечаем ссылку как используемую и привязываем к пользователю
    await vless_dao.update(
        VlessLinks.id == link_id,
        {
            "using": True,
            "user_id": user_id
        }
    )
    
    if trial_subscription:
        await trial_dao.update(
            TrialSubscription.user_id == user_id,
            {
                "start_date": current_date,
                "end_date": trial_end_date,
                "trial_used": True,
                "vless_link_id": link_id
            }
        )
    else:
        await trial_dao.create({
            "user_id": user_id,
            "start_date": current_date,
            "end_date": trial_end_date,
            "trial_used": True,
            "vless_link_id": link_id
        })
    
    logger.info(f"VLESS ссылка с id {link_id} привязана к пользователю {user_id}")

    link_to_user = f"tg://user?id={user_id}"
    try:
        await call.message.bot.send_message(
            chat_id=admin_id,
            text=f"Пользователь {markdown.hlink(str(user_id), link_to_user)} (@{username or 'без username'}) активировал пробный период на 3 дня\n\n"
                 f"VLESS ссылка: {markdown.hcode(vless_link)}\n"
                 f"ID ссылки: {link_id}\n"
                 f"Активировал: {markdown.hcode(current_date)}\n"
                 f"Истекает: {markdown.hcode(trial_end_date.strftime('%Y-%m-%d %H:%M:%S'))}"
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления админу о пробном периоде: {e}")
    
    await call.message.answer(
        text=f"Твой доступ к VPN готов 🚀\n\n"
             f"Вот твоя персональная ссылка (VLESS):\n\n"
             f"🔑 {markdown.hcode(vless_link)}\n\n"
             f"Как подключиться:\n"
             f"1. Скопируй ссылку\n"
             f"2. Вставь её в клиент (Happ, V2RayTun, Hiddify)\n"
             f"3. Подключайся и кайфуй от интернета без блокировок\n\n"
             f"Если не работает — пиши в поддержку"
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