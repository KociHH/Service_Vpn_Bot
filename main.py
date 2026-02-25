import asyncio
from contextlib import asynccontextmanager
import uvicorn
from aiogram import Dispatcher, Router, Bot
import logging
from aiogram.enums import ParseMode
from aiogram.types import Update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI
from fastapi.requests import Request
import settings
from db.middlewares.middle import DatabaseMiddleware, CheckSubcription
from db.tables import async_session, create_tables
from aiogram.client.bot import DefaultBotProperties
from commands import router as commands_router
from settings import BotParams
from utils.work import port, host, webhook

router = Router(name=__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

dp = Dispatcher()
dp.include_routers(commands_router)
bot = Bot(token=BotParams.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp.message.middleware(CheckSubcription(async_session))
dp.callback_query.middleware(CheckSubcription(async_session))
dp.update.middleware(DatabaseMiddleware(async_session))

webhook_bool = False
app = FastAPI()

if webhook_bool:
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
    
    if webhook_bool:
        uvicorn.run(app, host=host, port=port)
    else:
        asyncio.run(dp.start_polling(bot))

