from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional, Any

from pydantic import AnyUrl
from pydantic_settings import SettingsConfigDict, BaseSettings
from environs import Env

logger = logging.getLogger(__name__)
DEFAULT_EMAIL = "example@example.com"


@dataclass(frozen=True)
class client:
    Api_id: int
    Api_key: str


class YookassaToken:
    env: Env = Env()
    env.read_env()

    Api_id = env("API_ID")
    Api_key = env("API_KEY")

    Api_id_test = env("API_ID_TEST")
    Api_key_test = env("API_KEY_TEST")

# Имя: f1070382_termix
# Пользователь: f1070382_termix
# Пароль: 2551repP
# Адрес хоста: localhost



@dataclass(frozen=True)
class TG_bot:
    token: str
    admin_id: frozenset[int]
    webhook_url: str


@dataclass
class Config:
    tg_bot: TG_bot
    admin: TG_bot
    webhook: TG_bot


def load_path(path: str | None = None) -> Config:

    env: Env = Env()
    env.read_env(path)

    tg_bot = TG_bot(token=env('BOT_TOKEN'), admin_id=frozenset(map(int, env('ADMIN_IDS').split(','))), webhook_url=env('WEBHOOK_URL'))
    admin = TG_bot(token='', admin_id=frozenset(map(int, env('ADMIN_IDS').split(','))), webhook_url=env('WEBHOOK_URL'))
    webhook = TG_bot(token='', admin_id=frozenset(), webhook_url=env('WEBHOOK_URL'))

    return Config(tg_bot=tg_bot, admin=admin, webhook=webhook)


def Admins(path: int | None = None) -> set[int]:
    env: Env = Env()
    env.read_env(path)

    admin_ids_str = env('ADMIN_IDS')
    admin_ids = set(map(int, admin_ids_str.split(',')))
    return admin_ids


def WEBHOOK(path: str | None = None) -> dict[str, Any]:
    env: Env = Env()
    env.read_env(path)

    settings = {
        'port': env.int('PORT'),
        'host': env('HOST'),
        'WEBHOOK_URL': env('WEBHOOK_URL'),
        'WEBHOOK_PATH': env('WEBHOOK_PATH'),

        'WEBHOOK_URL_RENDER': env('WEBHOOK_URL_RENDER'),
        "WEBHOOK_URL_RAILWAY": env('WEBHOOK_URL_RAILWAY'),

        # uvicorn --port --host
        'HOST_RENDER': env('HOST_RENDER'),
        'PORT_RENDER': env.int('PORT_RENDER'),

        "HOST_RAILWAY": env('HOST_RAILWAY'),
        "PORT_RAILWAY": env.int('PORT_RAILWAY'),
    }
    return settings

# localhost
def SQl_localhost(path: Optional[str] = None) -> str:
    env: Env = Env()
    env.read_env(path)

    ip = env('IP')
    PASSWORD = env('PASSWORD')
    DATABASE = env('DATABASE')
    PGUSER = env('PGUSER')

    postgres_url = f'postgresql+asyncpg://{PGUSER}:{PASSWORD}@{ip}/{DATABASE}'

    return postgres_url

logger.info(SQl_localhost())

# railway
def SQL_URL(path: str | None = None) -> dict[str, AnyUrl | str]:
    env = Env()
    if path:
        env.read_env(path)
    else:
        env.read_env()

    urls_base = {
        "DATABASE_URL_PUBLIC": env('DATABASE_URL_PUBLIC'),
        "DATABASE_URL_PUBLIC_RENDER": env('DATABASE_URL_PUBLIC_RENDER'),
        'DATABASE_URL_PUBLIC_TIMEWEB': env('DATABASE_URL_PUBLIC_TIMEWEB'),
    }

    return urls_base
logger.info(SQL_URL())