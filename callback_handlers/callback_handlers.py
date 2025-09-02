import traceback
from typing import Optional, Union
from aiogram import F
from aiogram import Router
from aiogram.enums import ChatAction
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from FSM.states import Email
from FSM.validators_and_def import check_email, process_callback_data
from db.middlewares.middle import logger
from db.tables import user_dao, User
from keyboards.inline_keyboard.main_inline_keyboard import Main, Main_menu, Month_kb, return_kb_support, \
    Month, info2, info, info3, info_price_249, info_price_579, info_price_979, MonthCD
from keyboards.inline_keyboard.pay_inline_keyboard import CashMultiBt, CashMenu
from keyboards.reply_keyboard.state_reply import build_net_keyboard
from settings import DEFAULT_EMAIL, BotParams
from typing import Any

router = Router()

text_answer_one = markdown.text(
    f'🗝VPN на {info.month} месяц\n\n'
    f'📄Цена: {info.price} ₽\n\n'
    f'👤Кол-во устройств: ∞\n\n'
    '⚙️Всë необходимое будет предоставлено после приобретения', sep='\n')

text_answer_two = markdown.text(
    f'🗝VPN на {info2.month} месяца\n\n'
    f'📄Цена: {info2.price} ₽\n\n'
    f'👤Кол-во устройств: ∞\n\n'
    '⚙️Всë необходимое будет предоставлено после приобретения', sep='\n')

text_answer_tree = markdown.text(
    f'🗝VPN на {info3.month} месяцев\n\n'
    f'📄Цена: {info3.price} ₽\n\n'
    f'👤Кол-во устройств: ∞\n\n'
    '⚙️Всë необходимое будет предоставлено после приобретения', sep='\n')

text = markdown.text(
    markdown.hbold("Авторизация\n"),
    f"📨 Ведите почту для получения уведомления об оплате:\n\n"
    f"💡 Eсли вам это не нужно нажмите на кнопку ниже.", sep='\n'
)


# def valid_email_message_text(text: str) -> bool:
#     return bool(re.match(r"[^@]+@[^@]+\.[^@]+", text))


async def status_admin(user_id: int) -> str:
    user_id = str(user_id)

    if user_id in BotParams.admin_ids_str:
        return 'admin'
    return 'user'


async def upsert_user(
        call_and_message: Union[CallbackQuery, Message],
        email: Optional[str] = None
):

    name_user = call_and_message.from_user.full_name
    user_id = call_and_message.from_user.id

    existing = user_dao.get_one(User.user_id == user_id)

    if existing:
        updater = user_dao.update(
            User.user_id == user_id,
            {
                "user_id": user_id,
                "user_name": f"@{call_and_message.from_user.username}" if call_and_message.from_user.username else "Не указан",
                "full_name": call_and_message.from_user.full_name or "Невидимый ник" if not call_and_message.from_user.full_name else name_user,
                "email": email,
                "admin_status": await status_admin(user_id),
            },
        )
        if not updater:
            logger.error(f"Не обновился юзер {user_id}")
            return

    else:
        user_create = user_dao.create({
            "user_id": user_id,
            "user_name": f"@{call_and_message.from_user.username}" if call_and_message.from_user.username else "Не указан",
            "full_name": call_and_message.from_user.full_name or "Невидимый ник" if not call_and_message.from_user.full_name else name_user,
            "email": email,
            "admin_status": await status_admin(user_id),
        })
        if not user_create:
            logger.error(f"Не создался юзер {user_id}")
            return


async def _prompt_for_email(call: CallbackQuery, state: FSMContext, text: str):
    await state.set_state(Email.email)
    await call.answer()
    await call.message.answer(
        text=text,
        reply_markup=build_net_keyboard(),
    )
    await process_callback_data(call, state)


@router.callback_query(MonthCD.filter())
async def email_from(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    try:

        existing_user = await user_dao.get_one(User.user_id == user_id)

        if existing_user:
            if existing_user.email is None:
                await _prompt_for_email(call, state, text)

            else:
                await call.answer()
                await process_callback_data(call, state)
                await handle_month_subscription(call, state)
                await state.clear()

        else:
            await upsert_user(
                call_and_message=call,
                email=None
            )

            again_existing_user = await user_dao.get_one(User.user_id == user_id)

            if again_existing_user and again_existing_user.email is None:
                await _prompt_for_email(call, state, text)
            else:
                await call.answer('🛠 Проблемы ммм...', show_alert=True)

    except Exception as e:
        error_message = traceback.format_exc()
        logger.error(f"Ошибка: {error_message} и {e}")
        await call.answer(f"⚙️ Произошла ошибка, скоро исправим", show_alert=True)


@router.message(StateFilter(Email.email), F.text.casefold() == 'пропустить')
async def no_message(message: Message, state: FSMContext):
    await message.answer('Успешно!', reply_markup=ReplyKeyboardRemove())
    await state.update_data(email=DEFAULT_EMAIL)
    await upsert_user(
        call_and_message=message,
        email=DEFAULT_EMAIL,
    )

    await handle_month_subscription(message, state)
    await state.clear()
    return


@router.message(StateFilter(Email.email), F.text)
async def email_update(message: Message, state: FSMContext, ):
    email = message.text
    try:
            await message.bot.send_chat_action(
                chat_id=message.chat.id,
                action=ChatAction.TYPING,
            )
            await check_email(email=email, message=message)
            await upsert_user(
                call_and_message=message,
                email=email
            )

            await message.answer(f"Твой email {email} успешно сохранен!", reply_markup=ReplyKeyboardRemove())
            await handle_month_subscription(message, state)
            await state.clear()

    except Exception as e:
        logger.error(f'Ошибка при обработке email пользователя {e}')


async def handle_month_subscription(call_or_message: Union[CallbackQuery, Message], state: FSMContext):
    if isinstance(call_or_message, CallbackQuery):
        data = call_or_message.data
    elif isinstance(call_or_message, Message):
        state_data = await state.get_data()
        data = state_data.get("action")
    else:
        raise ValueError("Недопустимый тип ввода. Ожидаемый запрос CallbackQuery или Message")

    if not data:
        await call_or_message.answer("Ошибка: данные не найдены.")
        return

    if isinstance(data, str):
        try:
            callback_dict = {k: int(v) if k == 'month' else v for k, v in (item.split(':') for item in data.split(','))}
        except Exception as e:
            await call_or_message.answer(
                f"Ошибка при разборе данных В handle_month_subscription: {e}",
                show_alert=True)
            return

    elif isinstance(data, dict):
        callback_dict = data

    else:
        await call_or_message.answer("Ошибка: не поддерживаемый формат данных.", show_alert=True)
        return

    if 'month' in callback_dict:
        callback_dict['action'] = Month(callback_dict['month'])
    else:
        await call_or_message.answer("Ошибка: отсутствуют данные о месяце.", show_alert=True)
        return

    required_fields = ['month', 'action']
    if not all(field in callback_dict for field in required_fields):
        missing_fields = [field for field in required_fields if field not in callback_dict]
        await call_or_message.answer(f"Ошибка: отсутствуют данные: {', '.join(missing_fields)}.")
        return

    try:
        month_data = MonthCD(**callback_dict)
        action = month_data.action
    except Exception as e:
        await call_or_message.answer(
            f"Ошибка при разборе данных В handle_month_subscription: {str(e)}",
            show_alert=True
        )
        return

    if action == Month.One_month:
        callback_data_month = CashMenu.MOVEMENT_OPLATA
    elif action == Month.Two_month:
        callback_data_month = CashMenu.MOVEMENT_OPLATA_TWO
    elif action == Month.Tree_month:
        callback_data_month = CashMenu.MOVEMENT_OPLATA_TREE
    else:
        if isinstance(call_or_message, CallbackQuery):
            await call_or_message.answer("Неизвестное действие.", show_alert=True)
        elif isinstance(call_or_message, Message):
            await call_or_message.answer("Неизвестное действие.")
        return
    
    await handle_month(
        call_or_message,
        callback_data_month,
    )

async def handle_month(
        call_or_message: Union[CallbackQuery, Message],
        callback_data: Any,
        ):
    if isinstance(call_or_message, CallbackQuery):
        await call_or_message.answer()
        message = call_or_message.message
    elif isinstance(call_or_message, Message):
        message = call_or_message
    else:
        raise ValueError("Недопустимый тип ввода. Ожидаемый запрос CallbackQuery или Message")

    try:
        await message.answer(
            text=text_answer_one,
            reply_markup=CashMultiBt(callback_data)
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")


@router.callback_query(Main.MAIN)
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


@router.callback_query(Main.purchase)
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


@router.callback_query(Main.advantages)
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


@router.callback_query(Main.Support)
async def purchase_Support(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        text=markdown.text(
            f'💬 Если у вас возникли вопросы, смело обращайтесь в поддержку {markdown.hlink("AMMO VPN", url="https://t.me/ammosupport")}\n\n',
        ),
        reply_markup=return_kb_support())
