import traceback
from typing import Optional, Union

from aiogram import F
from aiogram import Router
from aiogram.enums import ChatAction
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from humanfriendly.terminal import message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from FSM.sates import Email
from FSM.validators_and_def import check_email, process_callback_data
from bd_api.middle import logger
from bd_api.middlewares.sa_tables import User, UserUpdater
from keyboards.inline_keyboard.main_inline_keyboard import Main, MainCD, Main_menu, Month_kb, return_kb_support, \
    MonthCD, Month, info2, info, info3
from keyboards.inline_keyboard.pay_inline_keyboard import Cash_Bt_Two, Cash_Bt_Tree, Cash_Bt
from keyboards.reply_keyboard.state_reply import build_net_keyboard
from settings import DEFAULT_EMAIL

router = Router()


# async def email(user_id: int, db_session: AsyncSession) -> Any | None:
#     result = await db_session.execute(select(User).where(User.user_id == user_id))
#     user = result.scalars().first()
#
#     if user:
#         return user.email
#     else:
#         return None


text_answer_one = markdown.text(
    f'🗝VPN на {info.month} месяц\n\n'
    f'📄Цена: {info.price} ₽\n\n'
    f'👤Кол-во устройств: {info.us}\n\n'
    '⚙️Всë необходимое будет предоставлено после приобретения\n\n'
    '❗️После приобретения необходимо обратиться в поддержку за получением инструкции по установке VPN - '
    '@ammosupport', sep='\n')

text_answer_two = markdown.text(
    f'🗝VPN на {info2.month} месяца\n\n'
    f'📄Цена: {info2.price} ₽\n\n'
    f'👤Кол-во устройств: {info2.us}\n\n'
    '⚙️Всë необходимое будет предоставлено после приобретения\n\n'
    '❗️После приобретения необходимо обратиться в поддержку за получением инструкции по установке VPN - '
    '@ammosupport', sep='\n')

text_answer_tree = markdown.text(
    f'🗝VPN на {info3.month} месяца\n\n'
    f'📄Цена: {info3.price} ₽\n\n'
    f'👤Кол-во устройств: {info3.us}\n\n'
    '⚙️Всë необходимое будет предоставлено после приобретения\n\n'
    '❗️После приобретения необходимо обратиться в поддержку за получением инструкции по установке VPN - '
    '@ammosupport', sep='\n')

text = markdown.text(
    markdown.hbold("Авторизация\n"),
    f"📨 Ведите почту для получения уведомления об оплате:\n\n"
    f"💡 Eсли вам это не нужно нажмите на кнопку ниже.", sep='\n'
)


# def valid_email_message_text(text: str) -> bool:
#     return bool(re.match(r"[^@]+@[^@]+\.[^@]+", text))


async def status_admin(db_session: AsyncSession, user_id: int) -> str:
    admins = tuple(settings.Admins())
    print(admins)

    result = await db_session.execute(select(User.admin_status).where(User.user_id == user_id, User.user_id.in_(admins)))
    if result.scalars().first():
        return 'admin'
    return 'user'


async def upsert_user(
        db_session: AsyncSession,
        call_and_message: Union[CallbackQuery, Message],
        email: Optional[str] = None
):

    name_user = call_and_message.from_user.full_name
    user_id = call_and_message.from_user.id

    # Поиск существующего пользователя
    query = await db_session.execute(select(User).where(User.user_id == user_id))
    existing_user = query.scalar_one_or_none()

    if existing_user:
        # Если пользователь существует, обновляем данные через UserUpdater
        updater = UserUpdater(
            existing_user,
            {
                "user_id": user_id,
                "user_name": f"@{call_and_message.from_user.username}" if call_and_message.from_user.username else "Не указан",
                "full_name": call_and_message.from_user.full_name or "Невидимый ник" if not call_and_message.from_user.full_name else name_user,
                "email": email,
                "admin_status": await status_admin(db_session, user_id),
            },
        )
        updater.update()
        await updater.save_to_db(db_session)

    else:
        # Если пользователь не найден, создаем нового
        new_user = User(
            user_id=user_id,
            user_name=f"@{call_and_message.from_user.username}" if call_and_message.from_user.username else "Не указан",
            full_name=call_and_message.from_user.full_name or "Невидимый ник" if not call_and_message.from_user.full_name else name_user,
            email=email,
            admin_status=await status_admin(db_session, user_id),
        )
        db_session.add(new_user)


@router.callback_query(MonthCD.filter())
async def email_from(call: CallbackQuery, db_session: AsyncSession, state: FSMContext):
    user_id = call.from_user.id

    try:
        await call.answer()

        result = await db_session.execute(select(User).where(User.user_id == user_id))
        existing_user = result.scalars().first()

        if existing_user:
            if existing_user.email is None:
                await state.set_state(Email.email)

                await call.message.answer(
                    text=text,
                    reply_markup=build_net_keyboard(),
                )
                await process_callback_data(call, state)

            else:
                await process_callback_data(call, state)
                await handle_month_subscription(call, state)
                await state.clear()

        else:
            await upsert_user(
                db_session=db_session,
                call_and_message=call,
                email=None
            )

            result = await db_session.execute(select(User).where(User.user_id == user_id))
            again_existing_user = result.scalars().first()

            if again_existing_user and again_existing_user.email is None:
                await state.set_state(Email.email)
                await call.message.answer(
                    text=text,
                    reply_markup=build_net_keyboard(),
                )
                await process_callback_data(call, state)
            else:
                await call.answer('🛠 Проблемы ммм...', show_alert=True)


    except Exception as e:
        error_message = traceback.format_exc()
        print(f"Ошибка: {error_message} и {e}")
        await call.answer(f"⚙️ Произошла ошибка, скоро исправим", show_alert=True)


@router.message(StateFilter(Email.email), F.text.casefold() == 'пропустить')
async def no_message(message: Message, db_session: AsyncSession, state: FSMContext):
    await message.answer('Успешно!', reply_markup=ReplyKeyboardRemove())
    await state.update_data(email=DEFAULT_EMAIL)
    await upsert_user(
        db_session=db_session,
        call_and_message=message,
        email=DEFAULT_EMAIL,
    )


    await handle_month_subscription(message, state)
    await state.clear()
    return


@router.message(StateFilter(Email.email), F.text)
async def email_update(message: Message, state: FSMContext, db_session: AsyncSession):
    email = message.text
    try:
            await message.bot.send_chat_action(
                chat_id=message.chat.id,
                action=ChatAction.TYPING,
            )

            await check_email(email=email, message=message)  # Проверяем формат email
            await upsert_user(
                db_session=db_session,
                call_and_message=message,
                email=email
            )

            await message.answer(f"Твой email {email} успешно сохранен!", reply_markup=ReplyKeyboardRemove())
            await handle_month_subscription(message, state)
            await state.clear()

    except Exception as e:
        raise e


async def handle_month_subscription(call_or_message: Union[CallbackQuery, Message], state: FSMContext):
    if isinstance(call_or_message, CallbackQuery):
        data = call_or_message.data
    elif isinstance(call_or_message, Message):
        state_data = await state.get_data()
        data = state_data.get("action")
    else:
        raise ValueError("Invalid input type. Expected CallbackQuery or Message.")
    print(f"Полученные данные до разборки: {data}")
    if not data:
        await call_or_message.answer("Ошибка: данные не найдены.")
        return

    if isinstance(data, str):
        try:
            callback_dict = {k: int(v) if k == 'month' else v for k, v in (item.split(':') for item in data.split(','))}
        except Exception as e:
            await call_or_message.answer(
                f"Ошибка при разборе данных В handle_month_subscription: {str(e)}",
                show_alert=True)
            return

    elif isinstance(data, dict):
        callback_dict = data

    else:
        await call_or_message.answer("Ошибка: не поддерживаемый формат данных.", show_alert=True)
        return

    print(f"еще: {callback_dict}")

    if 'month' in callback_dict:
        callback_dict['action'] = Month(callback_dict['month'])
    else:
        await call_or_message.answer("Ошибка: отсутствуют данные о месяце.", show_alert=True)
        return
    print(f"Полученные данные после разборки: {callback_dict}")

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

    print(f"Action: {action}")
    if action == Month.One_month:
        await handle_one_month(call_or_message)
    elif action == Month.Two_month:
        await handle_two_month(call_or_message)
    elif action == Month.Tree_month:
        await handle_three_month(call_or_message)
    else:

        if isinstance(call_or_message, CallbackQuery):
            await call_or_message.answer("Неизвестное действие.", show_alert=True)
        elif isinstance(call_or_message, Message):
            await call_or_message.answer("Неизвестное действие.")
    print(f"Action executed: {action}")


async def handle_one_month(call_or_message: Union[CallbackQuery, Message]):
    if isinstance(call_or_message, CallbackQuery):
        await call_or_message.answer()
        message = call_or_message.message
    elif isinstance(call_or_message, Message):
        message = call_or_message
    else:
        raise ValueError("Invalid input type. Expected CallbackQuery or Message.")

    try:
        await message.answer(
            text=text_answer_one,
            reply_markup=Cash_Bt()
        )
    except Exception as e:
        print(f"Error editing message: {e}")


async def handle_two_month(call_or_message: Union[CallbackQuery, Message]):
    if isinstance(call_or_message, CallbackQuery):
        await call_or_message.answer()
        message = call_or_message.message
    elif isinstance(call_or_message, Message):
        message = call_or_message
    else:
        raise ValueError("Invalid input type. Expected CallbackQuery or Message.")

    try:
        await message.answer(
            text=text_answer_two,
            reply_markup=Cash_Bt_Two()
        )
    except Exception as e:
        print(f"Error editing message: {e}")


async def handle_three_month(call_or_message: Union[CallbackQuery, Message]):
    if isinstance(call_or_message, CallbackQuery):
        await call_or_message.answer()
        message = call_or_message.message
    elif isinstance(call_or_message, Message):
        message = call_or_message
    else:
        raise ValueError("Invalid input type. Expected CallbackQuery or Message.")

    try:
        await message.answer(
            text=text_answer_tree,
            reply_markup=Cash_Bt_Tree()
        )
    except Exception as e:
        print(f"Error editing message: {e}")


@router.callback_query(
    MainCD.filter(F.action == Main.MAIN)
)
async def start(call: CallbackQuery):
    text = markdown.text(
        f"Привет, {call.from_user.full_name}!\n\n"
        "🪐Познакомьтесь с AMMO VPN:\n",
        "🌑 I Надежный клиент WireGuard\n",
        "💻 II Современный интерфейс\n",
        "🔎 III Непрерывная маскировка IP-адреса и безопасность\n",
        "💳Оплата картами РФ и СБП",
        sep='\n'
    )
    await call.message.edit_text(text, reply_markup=Main_menu())


@router.callback_query(
    MainCD.filter(F.action == Main.purchase)  # callback_data=MainCD(action=Main.purchase).pack()
)
async def purchase(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        text=markdown.text(
            '⏳VPN 1 месяц\n'
            'Описание:\n'
            'Цена: 179 ₽\n'
            'Кол-во устройств: 1\n\n'

            '⛓️VPN 2 месяца\n'
            'Описание:\n'
            'Цена: 329 ₽\n'
            'Кол-во устройств: 1\n\n'

            '🌪️VPN 3 месяца\n'
            'Описание:\n'
            'Цена: 449 ₽\n'
            'Кол-во устройств: 1\n\n'

            'Инструкция по установке прилагается вместе с VPN файлом',
            sep='\n'
        ),
        reply_markup=Month_kb()
    )


@router.callback_query(MainCD.filter(F.action == Main.advantages))
async def purchase_advantages(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        text=markdown.text(
            "🗝️AMMO VPN:\n\n"
            "🌑Обеспечит вас непрерывной маскировкой IP-адреса и безопасностью от отслеживания, перехватов и т. д.\n\n"
            "💻Современность AMMO VPN дает WireGuard, защита и интерфейс"), sep='\n',
        reply_markup=return_kb_support(),
    )


@router.callback_query(
    MainCD.filter(F.action == Main.Support),  # callback_data=MainCD(action=Main.Support).pack()
)
async def purchase_Support(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        text=markdown.text(
            "💬Если у вас возникли вопросы, смело обращайтесь в поддержку AMMO VPN - @ammosupport\n\n",

        ),
        reply_markup=return_kb_support())
