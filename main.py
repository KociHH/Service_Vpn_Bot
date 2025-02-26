import asyncio
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request, Depends
from aiogram import Dispatcher, Router, Bot
import logging
from aiogram.enums import ParseMode
from aiogram.loggers import webhook
from aiogram.types import Update
from aiohttp import web
from environs import Env
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from bd_api.middle import DatabaseMiddleware, async_session
from bd_api.middlewares.sa_tables import create_tables
from settings import Config, load_path
from aiogram.client.bot import DefaultBotProperties
from commands import router as commands_router
from utils.response_to_db import start_scheduler

router = Router(name=__name__)
logger = logging.getLogger(__name__)

webhook_fn = settings.WEBHOOK()
config: Config = load_path()

dp = Dispatcher()
dp.include_routers(commands_router)
bot = Bot(token=config.tg_bot.token,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp.update.middleware(DatabaseMiddleware(async_session))
logging.basicConfig(level=logging.INFO)

app = FastAPI()

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI, bot: Bot, db_session: AsyncSession):
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != webhook_fn['WEBHOOK_URL_RAILWAY']:
        await bot.set_webhook(webhook_fn['WEBHOOK_URL_RAILWAY'])
        await create_tables()
        asyncio.create_task(start_scheduler(bot, db_session))

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
    uvicorn.run(app, host=webhook_fn['HOST_RAILWAY'], port=webhook_fn['PORT_RAILWAY'])

