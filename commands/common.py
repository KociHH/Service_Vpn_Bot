import logging
import os.path
import random
from sys import prefix

from settings import Config, load_path
from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from aiogram.filters import Command, StateFilter
from aiogram import Router
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from FSM.sates import Admin
from bd_api.middlewares.sa_tables import User, Subscription
from keyboards.inline_keyboard.main_inline_keyboard import Main_menu, return_kb_support
from keyboards.reply_keyboard.admin_panel import admin_kb, rassilka_kb, yes_no_kb

router = Router()

# true admin if not admin false
def is_admin(message: Message) -> bool:
    return message.from_user.id in settings.Admins()

# main state if admin so admin panel
@router.message(Command('admin', prefix='/'))
async def admin(message: Message, state: FSMContext):
    await state.set_state(Admin.admin)
    if is_admin(message):
        await message.answer(
            '🔐 Вы администратор!',
        reply_markup=rassilka_kb()
        )

# state handler
@router.message(F.text == '📢 Рассылка')
async def rassilka(message: Message, state: FSMContext, db_session: AsyncSession):
    await state.set_state(Admin.rassilka)

    await message.answer(
        'Введите текст рассылки:',
        reply_markup=ReplyKeyboardRemove()
    )

# state handler
@router.message(StateFilter(Admin.rassilka))
async def edit_rassilka(message: Message, state: FSMContext, db_session: AsyncSession):
    await state.set_state(Admin.chek_rassilka)
    photo_id = message.photo[-1].file_id if message.photo else None
    gif_id = message.animation.file_id if message.animation else None
    await state.update_data({
        "text": message.text or None,
        "photo_id": photo_id,
        "caption": message.caption,
        "gif_id": gif_id
    })
    await message.answer(
        text=f'Вы уверены, что хотите отправить? Если нет то нажмите на кнопку [📝 Изменить текст]',
        reply_markup=yes_no_kb()
    )

samples = '________________________________'

# state handler
@router.message(StateFilter(Admin.chek_rassilka), F.text == 'Да')
async def rassilka_text(message: Message, state: FSMContext, db_session: AsyncSession):
    data = await state.get_data()
    text = data.get('text')
    photo_id = data.get('photo_id')
    caption = data.get('caption')
    gif_id = data.get('gif_id')


    users_count = await db_session.execute(select(func.count(User.id)))
    total_users = users_count.scalar()

    sent_count = 0
    error_count = 0

    users = await db_session.execute(select(User.user_id))
    for user in users.scalars():
        try:
            if photo_id:
                await message.bot.send_photo(
                    chat_id=user,
                    photo=photo_id,
                    caption=caption or text,
                    reply_markup=ReplyKeyboardRemove()
                )

            elif gif_id:
                await message.bot.send_animation(
                     chat_id=user,
                     animation=gif_id,
                     caption=caption or text,

                )
            else:
                await message.bot.send_message(
                    chat_id=user,
                    text=text
                )
            sent_count += 1

        except Exception as e:
            error_count += 1
            logging.error(f"Ошибка отправки сообщения пользователю {user}: {e}")



    # Отправляем итоговую статистику один раз после всех отправок
    await message.answer(
        f"📊 Статистика рассылки:\n"
        f"{samples}\n"
        f"👥 Всего пользователей:ㅤ{markdown.hbold(str(total_users))}\n"
        f"{samples}\n"
        f"✅ Успешно отправлено:ㅤ{markdown.hbold(str(sent_count))}\n"
        f"{samples}\n"
        f"❌ Ошибок:ㅤ{markdown.hbold(str(error_count))}",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

# state handler
@router.message(StateFilter(Admin.chek_rassilka), F.text == '📝 Изменить текст')
async def edit_text_rassilka(message: Message, state: FSMContext, db_session: AsyncSession):
    data = await state.get_data()
    photo_id = data.get('photo_id')
    text = data.get('text')
    caption = data.get('caption')
    gif_id = data.get('gif_id')

    if photo_id:
        await message.answer_photo(
            photo=photo_id,
            caption=f"{markdown.hbold('Текущее сообщение с фото:')}\n\n {caption or text}"
        )
    elif gif_id:
        await message.answer_animation(
            animation=gif_id,
            caption=f"{markdown.hbold('Текущее сообщение с GIF:')}\n\n {caption or text}"
    )
    else:
        await message.answer(
            text=f'{markdown.hbold("Текущее сообщение:")}\n\n{text}',
            reply_markup=ReplyKeyboardRemove()
        )

    await message.answer(
        'Введите исправный текст рассылки:',
        reply_markup=ReplyKeyboardRemove()
    )

    await state.set_state(Admin.rassilka)


@router.message(Command(commands=['start', 'help', 'admin', 'status']), StateFilter("*"))
async def handle_commands_in_state(message: Message, state: FSMContext, db_session: AsyncSession):

    if message.text == '/start':
        result = 'Вы вернулись в главное меню 👇'
    elif message.text == '/help':
        result = 'Вы вернулись в поддержку 👇'
    elif message.text == '/admin':
        result = 'Вы вернулись в /admin 👇'
    elif message.text == '/status':
        result = 'Вы вернулись в статистику 👇'
    else:
        result = 'Неизвестная команда'

    try:
        current_state = await state.get_state()


        if current_state is not None:
            await state.clear()
            await message.answer(
                result,
                reply_markup=ReplyKeyboardRemove()
            )

        command_handlers = {
            '/admin': admin,
            '/start': start_handler,
            '/help': lambda m, db_s: help_command(m),
            '/status': status_command,
        }

        if handler := command_handlers.get(message.text):
            await handler(message, db_session)
        else:
            logging.warning(f"Неизвестная команда: {message.text}")

    except Exception as e:
        logging.error(f"Ошибка при обработке команды {message.text}: {e}")
        await message.answer(
            "Произошла ошибка при выполнении команды",
            reply_markup=ReplyKeyboardRemove()
        )

# handler
@router.message(Command('start', prefix='/'))
async def start_handler(message: Message, db_session: AsyncSession):

    existing_user = await db_session.execute(
        select(User).where(User.user_id == message.from_user.id)
    )
    if not existing_user.scalar():
        user_id = User(user_id=message.from_user.id)
        db_session.add(user_id)
        await db_session.commit()

    text = markdown.text(
        f"Здравствуйте, {message.from_user.full_name}!\n\n"
        "🗝️ Познакомьтесь с AMMO VPN:\n",
        "🌑 I Скорость до 10 Гбит/с\n",
        "👁‍🗨 II Непрерывная маскировка IP-адреса и безопасность\n",
        "💻 III Современный интерфейс\n",
        "💳 Оплата картами РФ и СБП",
        sep='\n',

    )

    await message.answer(text, reply_markup=Main_menu())


@router.message(Command('status', prefix='/'))
async def status_command(message: Message, db_session: AsyncSession):
    chat_id = message.from_user.id
    result = await db_session.execute(select(Subscription).where(Subscription.user_id == chat_id).order_by(Subscription.end_date.desc()))
    subscription = result.scalars().first()

    if subscription:
        await message.answer(
            f"📄 Информация о вашей подписке:\n\n"
            f"{samples}\n"
            f"🗓 Последняя проведенная оплата: {subscription.start_date}\n"
            f"{samples}\n"
            f"📅 Дата окончания: {subscription.end_date}\n"
            f"{samples}\n"
            f"📌 Ваш статус: {'Активный' if subscription.status == 'active' else 'не активный'}\n"
        )
    else:
        await message.answer('🧐 Вы в данный момент не пользуютесь (пользовались) нашими услугами.')


@router.message(Command('help', prefix='/'))
async def help_command(message: Message):
    await message.answer(
        '💬 Если у вас возникли вопросы, смело обращайтесь в поддержку AMMO VPN - @ammosupport',
    )
