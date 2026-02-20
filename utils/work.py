from settings import WEBHOOK, SqlLocalhost, BotParams, RedisBD, SqlPublic
from kos_Htools.utils.time import DateTemplate
import logging
import os


logger = logging.getLogger(__name__)

# Принудительно устанавливаем TEST режим
mode = "TEST"

# Принудительно используем локальные настройки
webhook = WEBHOOK.WEBHOOK_URL
port = WEBHOOK.port
host = WEBHOOK.host

yookassa_bool = True
url_db = SqlLocalhost.postgres_url
username_support = BotParams.username_support_test
redis_url = RedisBD.LOCAL_REDIS
admin_id = BotParams.admin_id_test
    
url_support = f"https://t.me/{username_support}"

def currently_msk():
    return DateTemplate().conclusion_date(option="time_now").replace(tzinfo=None)

print(f"""
MODE: {mode} (FORCED TEST)
WEBHOOK: {webhook} 
PORT: {port}
HOST: {host}

DATABASE_URL: {url_db}
REDIS_URL: {redis_url} 

CURRENT_TIME: {currently_msk()}
SUPPORT_USER: {username_support}
SUPPORT_URL: {url_support}
""")
