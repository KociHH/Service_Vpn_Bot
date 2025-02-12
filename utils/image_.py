import io
import logging
import os
import random
import re
import subprocess
import zipfile
from os import error
from os.path import isdir

import rarfile
import redis
from aiogram.types import InputFile, BufferedInputFile, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton, \
    InlineKeyboardMarkup
from aiogram.utils import markdown
from rarfile import UNAR_TOOL
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from bd_api.middlewares.sa_tables import Images, Subscription
from utils.date_moscow import get_current_date, get_current_date_dis_mrk

logger = logging.getLogger(__name__)
UNRAR_PATH = r"C:\unrar\UnRAR.exe"
admin_id = os.getenv('ADMIN_ID')
nn = 'Неизвестно'
i = 0

async def db_checking_name(db_session: AsyncSession, message, file_full_name: str = None):
    req = await db_session.execute(select(Images).where(Images.name == file_full_name))
    existing_image = req.scalars().first()
    if existing_image:
        await message.answer(f"Братик такой файл как {markdown.hcode(file_full_name)} уже имеется, я его пропускаю ->")
        return False
    return True

async def save_img_to_db(images, db_session: AsyncSession):
    global i
    try:
        for name, img_data in images:
            while True:
                id_image = int(random.randint(1000000000, 9999999999))
                im = await db_session.execute(select(Images).where(Images.id_image == id_image))
                if not im.scalars().first():
                    image = Images(id_image=id_image, name=name, image=img_data)
                    db_session.add(image)
                    break
        await db_session.commit()
        logger.info(f'Сохранено {len(images)} изображений в БД. Кол-во: {i}')
    except Exception as e:
        logger.error(f'Ошибка в save_img_to_db: {e}')
        return []


async def image_extract(file_bytes: bytes, file_name: str, message, db_session: AsyncSession):
    global i
    try:
        images = []
        file_stream = io.BytesIO(file_bytes)

        if file_name.endswith('.zip'):
            with zipfile.ZipFile(file_stream, 'r') as archive:
                for file in archive.namelist():
                    if file.endswith('/'):
                        continue
                    if file.lower().endswith((".png", ".jpg", ".jpeg")):
                        if await db_checking_name(
                            file_full_name=file,
                            db_session=db_session,
                            message=message
                        ):
                            i += 1
                            with archive.open(file) as img_file:
                                images.append((file, img_file.read()))

        elif file_name.endswith('.rar'):
            rar_path = 'rar_save_.rar'
            with open('rar_save_.rar', 'wb') as save:
                save.write(file_bytes)

            command_list = [UNRAR_PATH, 'l', rar_path]
            process = subprocess.run(command_list, capture_output=True, text=True)
            file_list_ = process.stdout.splitlines()

            for line in file_list_:
                match = re.search(r'\s(\S+\.\w+)$', line)
                if not match:
                    continue
                file_name = str(match.group(1))
                file_full_name = str(os.path.basename(file_name))
                if 'rar_save_.rar' in file_full_name:
                    continue
                if await db_checking_name(
                    file_full_name=file_full_name,
                    db_session=db_session,
                    message=message
                ):
                    if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
                        i += 1
                        logger.info(f'Извлекаем - {file_name}, Который {i}')
                        command_extract = [UNRAR_PATH, "p", rar_path, file_name]
                        extract_process = subprocess.Popen(command_extract, stdout=subprocess.PIPE)
                        img_data, _ = extract_process.communicate()

                        if img_data:
                            images.append((file_full_name, img_data))
                    else:
                        await message.answer(f"В архиве нет воответствующих изображений.")

            os.remove(rar_path)
        return images, i

    except Exception as e:
        logger.error(f'Ошибка в image_extract: {e}')
        return [], i

async def count_images_db(message, db_session: AsyncSession):
    try:
        result = await db_session.execute(select(func.count()).select_from(Images))
        count = result.scalar()

        if count == 0:
            await message.answer(
                'Ничего не найдено, т.е изображения не были найдены.',
            )
        else:
            await message.answer(
                f'Изображений всего в БД = {markdown.hbold(count)}.',
            )
    except Exception as e:
        logger.error(f'Ошибка: {e}')


async def delete_code(message, db_session: AsyncSession, id_img: int):
    delete_ = await db_session.execute(delete(Images).where(Images.id_image == id_img))
    if delete_:
        logger.info('Фото успешно удалено')

    else:
        if isinstance(message, CallbackQuery):
            await message.message.answer('Не найдено существующих конфигураций на данный момент, обратитесь в поддержку - @ammosupport')
        else:
            await message.answer('Не найдено существующих конфигураций на данный момент, обратитесь в поддержку - @ammosupport')


async def send_crcode(message, db_session: AsyncSession, user_id: int):
    package_sub = []
    try:
        sub = await db_session.execute(select(Subscription).where(Subscription.user_id == user_id))
        src = sub.scalars().first()
        if src:
            start_date = src.start_date
            end_date = src.end_date
            package_sub.append((start_date, end_date))

        ch = await db_session.execute(select(Images).where(Images.id_image is not None))
        id_image = ch.scalars().first()

        if id_image:
            name = id_image.name
            id_img = id_image.id_image
            image_stream = id_image.image
            image_file = BufferedInputFile(image_stream, filename="AMMO_VPN.jpg")

            text = markdown.text(
                f"{markdown.hbold('I Установите WireGuard, сайт для скачивания -')}"
                f"{markdown.hlink('WireGuard',  'https://www.wireguard.com/install/')}\n\n"
                f"{markdown.hbold('II Отсканируйте или загрузите QR-Code')}\n\n"
                f"{markdown.hbold('III Добавьте туннель')}")

            await message.message.answer_photo(
                photo=image_file,
                caption=text
            )
            return name, id_img, package_sub
        else:
            name = nn
            id_img = nn
            keyboard = InlineKeyboardButton(
                text="🤝 Обратиться в поддержку",
                url='https://t.me/ammosupport'
            )
            button_support = InlineKeyboardMarkup(inline_keyboard=[[keyboard]])
            await message.message.answer(
                text=
                f'Извините, сейчас нет доступных ключей.\n'
                f'Нажмите на кнопку ниже, чтобы оповестить нас и мы выдадим новый ключ.',
                reply_markup=button_support
            )
            return name, id_img, package_sub


    except Exception as e:
        logger.error(f'Ошибка: {e}')
        return