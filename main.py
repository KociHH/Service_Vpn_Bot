import asyncio
from contextlib import asynccontextmanager
import uvicorn
from aiogram import Dispatcher, Router, Bot
import logging
from aiogram.enums import ParseMode
from aiogram.types import Update
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI
from fastapi.requests import Request
import settings
from db.middlewares.middle import DatabaseMiddleware, async_session
from db.tables import create_tables
from aiogram.client.bot import DefaultBotProperties
from commands import router as commands_router
from settings import BotParams
from utils.other import webhook, port, host

router = Router(name=__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dp = Dispatcher()
dp.include_routers(commands_router)
bot = Bot(token=BotParams.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp.update.middleware(DatabaseMiddleware(async_session))

def create_lifespan(bot: Bot):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        webhook_info = await bot.get_webhook_info()
        
        if webhook_info.url != webhook:
            logger.info("Bot started...")
            await bot.set_webhook(webhook)

        yield
        logger.info("Bot stopped...")
        await bot.delete_webhook()
        await bot.session.close()
    return lifespan

app = FastAPI(lifespan=create_lifespan(bot))

@app.post('/webhook')
async def bot_webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {'status': 'ok'}


if __name__ == "__main__":
    asyncio.run(create_tables())
    uvicorn.run(app, host=host, port=port)

