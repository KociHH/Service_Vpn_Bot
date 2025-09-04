import io
import logging
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from aiogram.filters import Command, StateFilter
from aiogram import Router
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from settings import BotParams
from FSM.states import Admin
from db.tables import User, Subscription, Images, PaymentHistory
from keyboards.inline_keyboard.main_inline_keyboard import Main_menu, slide_kb
from keyboards.reply_keyboard.admin_panel import admin_kb, main_menu_kb, yes_no_kb, yes_no, exit_
from utils.load_image import ImageProcessing
from utils.text_message import samples_
from utils.other import url_support
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from keyboards.reply_keyboard.buttons_names import MainButtons, NewsletterButtons
from aiogram.utils.deep_linking import decode_payload, create_start_link
from aiogram.client.bot import DefaultBotProperties
from aiogram import Bot
from aiogram.enums import ParseMode

router = Router()
logger = logging.getLogger(__name__)


def is_admin(message: Message) -> bool:
    return str(message.from_user.id) in [admin_id.strip() for admin_id in BotParams.admin_ids_str.split(',')]


@router.message(F.text == '⬅️ Вернуться', StateFilter("*"))
async def back(message: Message, state: FSMContext):
    await admin(message=message, state=state)


@router.message(Command('admin', prefix='/'))
async def admin(message: Message, state: FSMContext):
    await state.set_state(Admin.admin)
    if is_admin(message):
        await message.answer(
            '🔐 Вы администратор!',
        reply_markup=main_menu_kb()
        )


@router.message(F.text == MainButtons.check_images, StateFilter(Admin.admin))
async def check_image(message: Message, db_session: AsyncSession):
    image_utils = ImageProcessing(db_session)
    await image_utils.count_images_db(message)


@router.message(F.text == MainButtons.load_files, StateFilter(Admin.admin))
async def files(message: Message, state: FSMContext):
    await state.set_state(Admin.file)
    await message.answer(
        text=f"⛔️ Уточнение ⛔️\n"
             f" - Принимает только файлы формата: {markdown.hbold('.rar')} или {markdown.hbold('.zip')}.\n"
             f" - Присылайте строго по одному файлу за раз.\n"
             f" - Файл не должен содержать что то кроме изображений.\n"
             f" - Изображения должны различаться.\n"
             f" - Лимит на архив 10 мб",
        reply_markup=exit_()
    )
    await message.answer(
        text="Отправьте файл:"
    )


@router.message(StateFilter(Admin.file))
async def check_file(message: Message, state: FSMContext):
    MAX_FILE_SIZE = 10 * 1024 * 1024
    doc = message.document
    if message.photo and message.photo[-1]:
        await message.answer(
            text="Вы отправили фото, повторите попытку с файлом."
        )
    elif message.text:
        await message.answer(
            text="Вы отправили текст, повторите попытку с файлом."
        )
    elif doc:
        if doc.file_name.endswith(('.rar', '.zip')):
            if doc.file_size > MAX_FILE_SIZE:
                await message.answer(text="Я же говорил не больше 10 мб, изменяй")
                return

            file_id = doc.file_id
            file_name = doc.file_name
            if file_id and file_name:
                file = await message.bot.get_file(file_id)
                file_stream = io.BytesIO()
                await message.bot.download_file(file.file_path, file_stream)
                file_bytes = file_stream.getvalue()

                await state.update_data(
                    {
                    "file_bytes": file_bytes,
                    'file_name': file_name
                })
                await state.set_state(Admin.check_file)
                await message.answer(
                    text="Файл успешно обработан. Вы уверены, что хотите загрузить файл?",
                    reply_markup=yes_no()
            )
            else:
                await message.answer("Не удалось обработать файл.")
        else:
            await message.answer(
                text="Неверный формат файла, повторите попытку снова."
            )
    else:
        await message.answer(
            text="Вы не отправили файл, повторите попытку снова."
        )


@router.message(F.text == 'Да', StateFilter(Admin.check_file))
async def check_yes(message: Message, state: FSMContext, db_session: AsyncSession):
    img_data = await state.get_data()
    file_bytes = img_data.get('file_bytes')
    file_name = img_data.get('file_name')

    if file_bytes and file_name:
        image_utils = ImageProcessing(db_session)
        images, i = await image_utils.image_extract(
            file_bytes=file_bytes, 
            file_name=file_name, 
            message=message, 
            )
        if images:
            await image_utils.save_img_to_db(images)
            await message.answer(
                f'✅ Успешно загружено. Кол-во: {markdown.hbold(i)}',
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await message.answer(
                text='❗️ В архиве нет или не осталось изображений.',
                reply_markup=ReplyKeyboardRemove()
            )
    else:
        await message.answer(
            text='❌ Файл не найден.',
            reply_markup=ReplyKeyboardRemove()
        )

    await state.clear()


@router.message(F.text == 'Нет', StateFilter(Admin.check_file))
async def check_no(message: Message, state: FSMContext):
    await files(message, state)


@router.message(F.text == MainButtons.newsletter, StateFilter(Admin.admin))
async def rassilka(message: Message, state: FSMContext,):
    await state.set_state(Admin.rassilka)

    await message.answer(
        'Введите текст рассылки:',
        reply_markup=exit_()
    )


@router.message(StateFilter(Admin.rassilka))
async def edit_rassilka(message: Message, state: FSMContext,):
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

@router.message(StateFilter(Admin.chek_rassilka), F.text == 'Да')
async def rassilka_text(message: Message, state: FSMContext, db_session: AsyncSession):
    data = await state.get_data()
    text = data.get('text')
    photo_id = data.get('photo_id')
    caption = data.get('caption')
    gif_id = data.get('gif_id')

    sent_count = 0
    error_count = 0

    user_dao = BaseDAO(User, db_session)
    total_users = await len(user_dao.get_all_column_values(User.user_id))
    for user in total_users:
        await asyncio.sleep(0.2)
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


    await message.answer(
        f"📊 Статистика рассылки:\n"
        f"{samples}\n"
        f"👥 Всего пользователей:ㅤ{markdown.hbold(str(total_users))}\n"
        f"{samples}\n"
        f"✅ Успешно отправлено:ㅤ{markdown.hbold(str(sent_count))}\n"
        f"{samples}\n"
        f"❌ Не было отправленно:ㅤ{markdown.hbold(str(error_count))}",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@router.message(StateFilter(Admin.chek_rassilka), F.text == NewsletterButtons.change_text)
async def edit_text_rassilka(message: Message, state: FSMContext):
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


@router.message(F.text == MainButtons.info_payments, StateFilter(Admin.admin))
async def output_users(state: FSMContext, message: Message, db_session: AsyncSession):
    pay_dao = BaseDAO(PaymentHistory, db_session)
    check_users = await pay_dao.get_all_column_values(PaymentHistory.user_id)
    max_users = 10
    bot = Bot(token=BotParams.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    if not check_users:
        await message.answer(text="🤷‍♂️ Нет ни одной транзакции от юзеров.")
        return

    text = check_users
    if len(check_users) > max_users:
        text = check_users[:max_users]

    result_text = ''
    for uid in text:
        link = await create_start_link(bot=bot, payload=f"payments_{uid}", encode=True)
        result_text += f"\n{markdown.hlink(uid, url=link)}"

    if not result_text:
        logger.error("В переменную result_text ничего не было добавленно, в функции output_users.")
        return

    await message.answer(
        text=
        f"Список юзеров VPN. Нажмите на ссылку ввиде его id, чтобы увидеть все транзакции юзера:\n\n {result_text}",
        reply_markup=slide_kb(2)
    )


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
            '/help': help_command,
            '/status': status_command,
        }

        if handler := command_handlers.get(message.text):
            if message.text in ['/admin', '/start', '/status', '/help']:
                if message.text == '/admin':
                    await handler(message, state)
                elif message.text in ['/start', "/status"]:
                    await handler(message, db_session)
                elif message.text == '/help':
                    await handler(message)
        else:
            logging.warning(f"Неизвестная команда: {message.text}")

    except Exception as e:
        logging.error(f"Ошибка при обработке команды {message.text}: {e}")
        await message.answer(
            "Произошла ошибка при выполнении команды",
            reply_markup=ReplyKeyboardRemove()
        )

async def status_admin(user_id: int) -> str:
    user_id = str(user_id)

    if user_id in BotParams.admin_ids_str:
        return 'admin'
    return 'user'


@router.message(Command('start', prefix='/'))
async def start_handler(message: Message, db_session: AsyncSession):
    user_id = message.from_user.id
    name_user = message.from_user.full_name
    username = message.from_user.username

    user_dao = BaseDAO(User, db_session)
    existing = await user_dao.get_one(User.user_id == user_id)

    user_save = {
        "user_name": username if username else "Не указан",
        "full_name": name_user or "Невидимый ник",
        "admin_status": await status_admin(user_id),
    }

    if existing:
        updater = await user_dao.update(
            User.user_id == user_id,
            user_save,
        )
        if not updater:
            logger.error(f"Не обновился юзер {user_id}")
            return

    else:
        user_save["user_id"] = user_id
        user_create = await user_dao.create(user_save)
        if not user_create:
            logger.error(f"Не создался юзер {user_id}")
            return

    text = markdown.text(
        f"Здравствуйте, {message.from_user.full_name}!\n\n"
        f"🗝️ Познакомьтесь с {BotParams.name_project}:\n",
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

    sub_dao = BaseDAO(Subscription, db_session)
    subscription = await sub_dao.get_one(Subscription.user_id == chat_id)

    if subscription:
        l = [
            "📄 Информация о вашей подписке:",
            f"🗓 Дата первой оплаты: {markdown.hcode(subscription.start_date)}",
            f"📅 Дата окончания: {markdown.hcode(subscription.end_date)}",
            f"📌 Ваш статус: {markdown.hcode('Активный' if subscription.status == 'active' else 'Не активный')}"]
        await message.answer(
            await samples_(l)
        )
    else:
        await message.answer('🧐 Вы в данный момент не пользуютесь (пользовались) нашими услугами.')


@router.message(Command('help', prefix='/'))
async def help_command(message: Message):
    await message.answer(
        text=markdown.text(
            f'💬 Если у вас возникли вопросы, смело обращайтесь в поддержку {markdown.hlink(title=BotParams.name_project, url=url_support)}\n\n',
        ),
    )


@router.message(F.text.func(lambda t: t and t.startswith("/start")))
async def start_deep_link(message: Message, db_session: AsyncSession):
    args = message.text.split(maxsplit=1)
    happening = None

    if len(args) < 2:
        logger.error("Ошибка не правильная deep ссылка")
        return
    
    happening = decode_payload(args[13])
    if happening:
        if happening.startswith("payments_"):
            user_id = int(happening.split("_")[13])
            pay_dao = BaseDAO(PaymentHistory, db_session)
            find_user = await pay_dao.get_one(
                (PaymentHistory.user_id == user_id,
                 PaymentHistory.payment_amount,
                 PaymentHistory.date_paid))

            max_payment = 10
            paylen = len(find_user.payment_amount)
            payments = find_user.payment_amount
            reply_markup = False

            if paylen > max_payment:
                payments = find_user.payment_amount[:paylen]
                reply_markup = True

            result_text = ''
            for pay in payments:
                result_text += f"\n{pay} | {find_user.date_paid}"

            if not result_text:
                logger.error("В переменную result_text ничего не было добавленно, в функции start_deep_link.")
                return

            if find_user:
                if reply_markup:
                    await message.answer(
                        text=result_text,
                        reply_markup=slide_kb(2)
                    )
                else:
                    await message.answer(
                        text=result_text
                    )
    
    await message.answer("Добро пожаловать!")