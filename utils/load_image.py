import io
import logging
import os
import random
import re
import subprocess
import zipfile
from db.middlewares.middle import async_session
from aiogram.types import InputFile, BufferedInputFile, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton, \
    InlineKeyboardMarkup
from aiogram.utils import markdown
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from db.tables import Images, Subscription, images_dao, sub_dao

logger = logging.getLogger(__name__)
UNRAR_PATH = r"C:\unrar\UnRAR.exe"
admin_id = os.getenv('ADMIN_ID')


class ImageProcessing:
    def __init__(self):
        self.i = 0

    async def db_checking_img_data(self, message, img_data: str, file_name: str):
        output_image = await images_dao.get_one(Images.image == img_data)
        if output_image:
            await message.answer(f"Такое изображение как {markdown.hcode(file_name)} уже имеется, я его пропускаю ->")
            return False
        return True

    async def save_img_to_db(self, images):
        try:
            saved = len(images)
            for name, img_data in images:
                while True:
                    existing_img = await images_dao.get_one(Images.image == img_data)
                    if existing_img:
                        logger.info("Есть похожий qrcode пропускаю..")
                        saved -= 1
                        break

                    image_created = await images_dao.create({
                        "name": name,
                        "image": img_data,
                    })

                    if not image_created:
                        logger.error(f"Ошибка при сохранении qrcode (name: {name})")
                        saved -= 1
                    break

            logger.info(f'Успешно сохранено {saved} изоб.; не были сохранены: {len(images) - saved} изоб.')
            return
        except Exception as e:
            logger.error(f'Ошибка в save_img_to_db: {e}')
            return


    async def image_extract(self, file_bytes: bytes, file_name: str, message):
        try:
            images = []
            file_stream = io.BytesIO(file_bytes)

            if file_name.endswith('.zip'):
                with zipfile.ZipFile(file_stream, 'r') as archive:
                    for file in archive.namelist():
                        if file.endswith('/'):
                            continue
                        if file.lower().endswith((".png", ".jpg", ".jpeg")):
                            if await self.db_checking_img_data(
                                file_name=file,
                                img_data=img_file.read(),
                                message=message
                            ):
                                self.i += 1
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

                    if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
                        self.i += 1
                        logger.info(f'Извлекаем - {file_full_name}, Который {self.i}')
                        command_extract = [UNRAR_PATH, "p", rar_path, file_name]
                        extract_process = subprocess.Popen(command_extract, stdout=subprocess.PIPE)
                        img_data, _ = extract_process.communicate()

                        if img_data:
                            if await self.db_checking_img_data(
                                file_name=file_full_name,
                                img_data=img_data,
                                message=message
                            ):
                                images.append((file_full_name, img_data))
                    else:
                        await message.answer(f"В архиве нет соответствующих изображений.")

                os.remove(rar_path)
            return images, self.i

        except Exception as e:
            logger.error(f'Ошибка в image_extract: {e}')
            return [], self.i


    async def count_images_db(self, message: CallbackQuery):
        try:
            count = await len(images_dao.get_all_column_values(Images.id))

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


    async def delete_code(self, message, id_img: int):
        delete_img = await self.image_dao.delete(Images.id == id_img)
        if delete_img:
            logger.info('Фото успешно удалено')

        else:
            if isinstance(message, CallbackQuery):
                await message.message.answer('Не найдено существующих конфигураций на данный момент, обратитесь в поддержку - @ammosupport')
            else:
                await message.answer('Не найдено существующих конфигураций на данный момент, обратитесь в поддержку - @ammosupport')


    async def send_crcode(self, message: CallbackQuery, user_id: int):
        package_sub = []
        try:
            src = await self.image_dao.get_one(Subscription.user_id == user_id)
            if src:
                start_date = src.start_date
                end_date = src.end_date
                package_sub.append((start_date, end_date))

            output_image = await self.image_dao.get_one(Images.id is not None)

            if output_image:
                name = output_image.name
                id_img = output_image.id
                image_stream = output_image.image
                image_file = BufferedInputFile(image_stream, filename="AMMO_VPN.jpg")

                text = markdown.text(
                    f"Инструкция:\n\n"

                    "I Установите WireGuard\n"
                    "ссылка на сайт для скачивания - https://www.wireguard.com/install/\n"
                    "II Войдя в WireGuard нажмите на '+' и сканируйте QR-код, который Вам выдал бот\n\n"

                    "I Не делитесь своими данными VPN с посторонними\n"
                    "II Не используйте 1 приобретенный ключ на разных устройствах,\n"
                    "лучше приобрести новый vpn для другого устройства\n"
                    "III Не забывайте выходить из VPN, когда он вам не нужен\n\n"

                    "Желаем Вам приятного использования AMMO VPN!",
                )

                await message.message.answer_photo(
                    photo=image_file,
                    caption=text
                )

                return name, id_img, package_sub
            else:
                name = 'Неизвестно'
                id_img = 'Неизвестно'
                keyboard = InlineKeyboardButton(
                    text="🤝 Обратиться в поддержку",
                    url='https://t.me/tripleswaga'
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