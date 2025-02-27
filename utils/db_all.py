import asyncio
import logging

from bd_api.middlewares.sa_tables import create_tables
logger = logging.getLogger(__name__)

async def init_db():
    await create_tables()
    logger.info("Tables created")

asyncio.run(init_db())