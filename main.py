import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
import requests
from aiogram import Dispatcher, Router, Bot
import logging
from aiogram.enums import ParseMode
from aiogram.loggers import webhook
from aiogram.types import Update
from aiohttp import web
from environs import Env

import settings
from bd_api.middle import DatabaseMiddleware, async_session
from settings import Config, load_path
from aiogram.client.bot import DefaultBotProperties
from commands import router as commands_router

router = Router(name=__name__)


webhook_fn = settings.WEBHOOK()
config: Config = load_path()

dp = Dispatcher()
dp.include_routers(commands_router)
dp.update.middleware(DatabaseMiddleware(async_session))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.tg_bot.token,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != webhook_fn['WEBHOOK_URL']:
        await bot.set_webhook(webhook_fn['WEBHOOK_URL'])
    yield
    await bot.delete_webhook()
    await bot.session.close()

app.lifespan = lifespan

@app.post('/webhook')
async def bot_webhook(request: Request):
    data = await request.json()
    update = Update(**data)

    await dp.feed_update(bot, update)
    return {'status': 'ok'}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=webhook_fn['host'], port=webhook_fn['port'])


# print(webhook_fn['WEBHOOK_URL'], webhook_fn['port'], webhook_fn['host'])
#
# # Установка вебхука
# async def webhook_setup(bot: Bot):
#     webhook_url = webhook_fn['WEBHOOK_URL'] + '/webhook'
#     await bot.set_webhook(webhook_url)
#
#
# async def handle_webhook(request):
#
#     # получение данных от телеграм
#     data = await request.json()
#     update = Update(**data)
#     print("Update:", data)
#
#     # Передача обновления в диспетчер
#     await dp.feed_update(bot, update)
#     return web.Response(text='OK')
#
#
# # основная функция
# async def main():
#     await webhook_setup(bot)
#
#     # Создание aiohttp-приложения
#     app = web.Application()
#     app.router.add_post('/webhook', handle_webhook)
#
#     # запуск сервера
#     runner = web.AppRunner(app)
#     await runner.setup()
#     site = web.TCPSite(runner, host=webhook_fn['host'], port=webhook_fn['port'])
#     await site.start()
#
#     print(f"Запущен сервер на {webhook_fn['port']}:{webhook_fn['host']}")
#
#
#     # блокировка для работы сервера
#     try:
#         await asyncio.Event().wait()
#     except KeyboardInterrupt:
#         await runner.cleanup()



# if __name__ == '__main__':
#     asyncio.run(main())
