from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional

from pydantic_settings import SettingsConfigDict, BaseSettings
from environs import Env
DEFAULT_EMAIL = "example@example.com"

host = 'localhost'
user = 'postgres'
password = 'patcher2244'
db_name = 'postgres'


@dataclass(frozen=True)
class client:
    Api_id: int
    Api_key: str



class YookassaToken:
    Api_id = '990319'
    Api_key = 'live_Howy2o7x8lL1o7kEpqaWuOihNxKTmzZSkrLo4nsL0ps'

    Api_id_test = '993051'
    Api_key_test = 'test_Z5NnY5EXR4G9rBR1FkXwRIbHbxw1H3ajQ5AjGSIp2NY'


@dataclass(frozen=True)
class TG_bot:
    token: str
    admin_id: frozenset[int]


@dataclass
class Config:
    tg_bot: TG_bot
    admin: TG_bot


def load_path(path: str | None = None) -> Config:

    env: Env = Env()
    env.read_env(path)

    tg_bot = TG_bot(token=env('BOT_TOKEN'), admin_id=frozenset())  # Инициализация объекта TG_bot для tg_bot
    admin = TG_bot(token='', admin_id=frozenset(map(int, env('ADMIN_IDS').split(','))))

    return Config(tg_bot=tg_bot, admin=admin)


def Admins(path: int | None = None) -> set[int]:
    env: Env = Env()
    env.read_env(path)

    admin_ids_str = env('ADMIN_IDS')
    admin_ids = set(map(int, admin_ids_str.split(',')))
    return admin_ids


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
