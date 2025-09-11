from __future__ import annotations

import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
DEFAULT_EMAIL = "example@example.com"
load_dotenv()

class YookassaToken:
    Api_id = os.getenv("API_ID")
    Api_key = os.getenv("API_KEY")

    Api_id_test = os.getenv("API_ID_TEST")
    Api_key_test = os.getenv("API_KEY_TEST")

class BotParams:
    admin_ids_str = os.getenv('ADMIN_IDS')
    bot_token = os.getenv("BOT_TOKEN")
    username_support = os.getenv("USERNAME_SUPPORT")
    username_channel = os.getenv("USERNAME_CHANNEL")
    username_support_test = os.getenv("USERNAME_SUPPORT_TEST")
    name_project = os.getenv("NAME_PROJECT")
    admin_id_test = os.getenv("ADMIN_ID_TEST")
    admin_id_prod = os.getenv("ADMIN_ID")
    username_bot = os.getenv("USERNAME_BOT")

class WEBHOOK:
    port = int(os.getenv('PORT'))
    host = os.getenv('HOST')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')

    WEBHOOK_PATH_TIMEWEB = os.getenv('WEBHOOK_PATH_TIMEWEB')
    host_TIMEWEB = os.getenv("HOST_TIMEWEB")
    port_TIMEWEB = int(os.getenv("PORT_TIMEWEB"))

class SqlLocalhost:
    ip = os.getenv('IP')
    PASSWORD = os.getenv('PASSWORD')
    DATABASE = os.getenv('DATABASE')
    PGUSER = os.getenv('PGUSER')

    postgres_url = f'postgresql+asyncpg://{PGUSER}:{PASSWORD}@{ip}/{DATABASE}'

logger.info(SqlLocalhost.postgres_url)

class SqlPublic:
    DATABASE_URL_PUBLIC = os.getenv("DATABASE_URL_PUBLIC")

class RedisBD:
    LOCAL_REDIS = os.getenv("LOCAL_REDIS")
    PROD_REDIS = os.getenv("PROD_REDIS")

class SqlUrlService:
    urls_base = {
        'DATABASE_URL_PUBLIC_TIMEWEB': os.getenv('DATABASE_URL_PUBLIC_TIMEWEB'),
    }

logger.info(SqlUrlService.urls_base)