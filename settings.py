from __future__ import annotations

import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
DEFAULT_EMAIL = "example@example.com"
load_dotenv()
env = os.getenv()

class YookassaToken:
    Api_id = env("API_ID")
    Api_key = env("API_KEY")

    Api_id_test = env("API_ID_TEST")
    Api_key_test = env("API_KEY_TEST")

class BotParams:
    admin_ids_str = env('ADMIN_IDS')
    bot_token = env("BOT_TOKEN")
    username_support = env("USERNAME_SUPPORT")
    username_channel = env("USERNAME_CHANNEL")
    username_support_test = env("USERNAME_SUPPORT_TEST")
    name_project = env("NAME_PROJECT")

class WEBHOOK:
    port = int(env('PORT')),
    host = env('HOST'),
    WEBHOOK_URL = env('WEBHOOK_URL'),
    WEBHOOK_PATH = env('WEBHOOK_PATH'),
    WEBHOOK_PATH_TIMEWEB = env('WEBHOOK_PATH_TIMEWEB'),
    WEBHOOK_URL_RENDER = env('WEBHOOK_URL_RENDER'),
    WEBHOOK_URL_RAILWAY = env('WEBHOOK_URL_RAILWAY'),

    # uvicorn --port --host
    HOST_RENDER = env('HOST_RENDER'),
    PORT_RENDER = int(env('PORT_RENDER')),

    HOST_RAILWAY = env('HOST_RAILWAY'),
    PORT_RAILWAY = int(env('PORT_RAILWAY')),


class SqlLocalhost:
    ip = env('IP')
    PASSWORD = env('PASSWORD')
    DATABASE = env('DATABASE')
    PGUSER = env('PGUSER')

    postgres_url = f'postgresql+asyncpg://{PGUSER}:{PASSWORD}@{ip}/{DATABASE}'

logger.info(SqlLocalhost.postgres_url)

class RedisBD:
    LOCAL_REDIS = env("LOCAL_REDIS")
    PROD_REDIS = env("PROD_REDIS")

class SqlUrlService:
    urls_base = {
        "DATABASE_URL_PUBLIC": env('DATABASE_URL_PUBLIC'),
        "DATABASE_URL_PUBLIC_RENDER": env('DATABASE_URL_PUBLIC_RENDER'),
        'DATABASE_URL_PUBLIC_TIMEWEB': env('DATABASE_URL_PUBLIC_TIMEWEB'),
    }

logger.info(SqlUrlService.urls_base)