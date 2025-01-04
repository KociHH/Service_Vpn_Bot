from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional

from pydantic import AnyUrl
from pydantic_settings import SettingsConfigDict, BaseSettings
from environs import Env


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


def WEBHOOK(path: str | None = None):
    env: Env = Env()
    env.read_env(path)

    settings = {
        'port': env.int('PORT'),
        'host': env('HOST'),
        'WEBHOOK_URL': env('WEBHOOK_URL'),
        'WEBHOOK_PATH': env('WEBHOOK_PATH'),
    }
    return settings


def SQlpg(path: Optional[str] = None) -> str:
    env: Env = Env()
    env.read_env(path)

    ip = env('IP')
    PASSWORD = env('PASSWORD')
    DATABASE = env('DATABASE')
    PGUSER = env('PGUSER')

    postgres_url = f'postgresql+asyncpg://{PGUSER}:{PASSWORD}@{ip}/{DATABASE}'

    return postgres_url

print(SQlpg())

# @dataclass
# class Admin_id:
#     admin_id: frozenset[int]
#
#
# @dataclass
# class Admins:
#     admins: Admin_id
#
#
# admin_ids = Admin_id(admin_id=frozenset({5537454918, 1896661232, 1958773156}))
# admins = Admins(admins=admin_ids)



# class Settings(BaseSettings):
#     model_config = SettingsConfigDict(
#         case_sensitive=False,
#     )
#
#     bot_token: str
#     admin_id: frozenset[int] = frozenset({5537454918, 1896661232, 1958773156})
#
#
#
# settings = Settings()
