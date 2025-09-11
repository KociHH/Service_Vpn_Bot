from settings import WEBHOOK, SqlLocalhost, BotParams, RedisBD, SqlPublic
from kos_Htools.utils.time import DateTemplate
import logging


logger = logging.getLogger(__name__)

# TEST | PROD

mode = "TEST"

if mode == "TEST":
    webhook = WEBHOOK.WEBHOOK_URL
    port = WEBHOOK.port
    host = WEBHOOK.host

    yookassa_bool = True
    url_db = SqlLocalhost.postgres_url
    username_support = BotParams.username_support_test
    redis_url = RedisBD.LOCAL_REDIS
    admin_id = BotParams.admin_id_test

elif mode == "PROD":
    webhook = WEBHOOK.WEBHOOK_PATH_TIMEWEB
    port = WEBHOOK.port_TIMEWEB   
    host = WEBHOOK.host_TIMEWEB

    yookassa_bool = False
    url_db = SqlPublic.DATABASE_URL_PUBLIC
    username_support = BotParams.username_support
    redis_url = RedisBD.PROD_REDIS
    admin_id = BotParams.admin_id_prod
    
url_support = f"https://t.me/{username_support}"

def currently_msk():
    return DateTemplate().conclusion_date(option="time_now").replace(tzinfo=None)

print(f"""
{webhook} 
{port}
{host}

{url_db}
{redis_url} 

{currently_msk()}
{username_support}
{url_support}
""")
