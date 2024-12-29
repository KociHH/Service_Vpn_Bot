import asyncio

import requests
from aiogram import Dispatcher, Router, Bot
import logging
from aiogram.enums import ParseMode
from aiogram.types import Update

from bd_api.middle import DatabaseMiddleware, async_session
from settings import Config, load_path
from aiogram.client.bot import DefaultBotProperties
from commands import router as commands_router

config: Config = load_path()

router = Router(name=__name__)

async def main():
    dp = Dispatcher()

    dp.include_routers(commands_router)
    dp.update.middleware(DatabaseMiddleware(async_session))


    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.tg_bot.token,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
