import logging
import os.path
import random
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
from bd_api.middlewares.sa_tables import User
from keyboards.inline_keyboard.main_inline_keyboard import Main_menu, return_kb_support
from keyboards.reply_keyboard.admin_panel import admin_kb, rassilka_kb, yes_no_kb

router = Router()
file_id = 'CAACAgIAAxkBAAENPehnSaTAff8Bp2seJXVgdaalTXS-lwACnA0AArrNuUrJQaN_QYSCkDYE'

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
    print(text, caption)

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


# the handler resets whether there is a state
@router.message(Command(commands=['start', 'help', 'admin']), StateFilter("*"))
async def handle_commands_in_state(message: Message, state: FSMContext):

    # words = ['♻ Клавиатура удалена', '❓ Состояние сброшено']
    # generator = dict(enumerate(words))
    #
    # def gen():
    #     keys = list(generator.keys())
    #     random_key = random.choice(keys)
    #
    #     return generator[random_key]
    #
    # result = gen()

    if message.text == '/start':
        result = 'Вы вернулись в главное меню 👇'
    elif message.text == '/help':
        result = 'Вы вернулись в поддержку 👇'
    elif message.text == '/admin':
        result = 'Вы вернулись в /admin 👇'
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
            '/help': help
        }

        if handler := command_handlers.get(message.text):
            await handler(message)
        else:
            print(f"Неизвестная команда: {message.text}")

    except Exception as e:
        print(f"Ошибка при обработке команды {message.text}: {e}")
        logging.error(f"Ошибка при обработке команды {message.text}: {e}")
        await message.answer(
            "Произошла ошибка при выполнении команды",
            reply_markup=ReplyKeyboardRemove()
        )


# handler
@router.message(Command('start', prefix='/'))
async def start_handler(message: Message):

    text = markdown.text(
        f"Привет, {message.from_user.full_name}!\n\n"
        "🪐 Познакомьтесь с AMMO VPN:\n",
        "🌑 I Надежный клиент WireGuard\n",
        "💻 II Современный интерфейс\n",
        "🔎 III Непрерывная маскировка IP-адреса и безопасность\n",
        "💳 Оплата картами РФ и СБП",
        sep='\n',

    )

    await message.answer(text, reply_markup=Main_menu())

# handler
@router.message(Command('help', prefix='/'))
async def help(message: Message):
    await message.answer(
        '💬Если у вас возникли вопросы, смело обращайтесь в поддержку AMMO VPN - @ammosupport',
        reply_markup=return_kb_support()
    )


path = "./img"
config: Config = load_path()
bot = Bot(config.tg_bot.token)


# saves the sent photo
@router.message(F.photo)
async def handle_photo(message: types.Message):

    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)

    file_name = f"{file_info.file_unique_id}.png"
    file_path = os.path.join(path, file_name)

    if os.path.exists(file_path):
        print(f"Фотография с именем {file_name} уже существует.")
        return


    await bot.download_file(file_info.file_path, destination=file_path)
    print(f"Фотография сохранена как {file_name}!")
