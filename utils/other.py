from settings import WEBHOOK, SqlLocalhost, SqlUrlService, BotParams, RedisBD
from kos_Htools.utils.time import DateTemplate
import logging

logger = logging.getLogger(__name__)

# TEST | PROD

mode = "TEST"

if mode == "TEST":
    webhook = WEBHOOK.WEBHOOK_URL
    url_db = SqlLocalhost.postgres_url
    username_support = BotParams.username_support_test
    redis_url = RedisBD.LOCAL_REDIS

elif mode == "PROD":
    webhook = WEBHOOK.WEBHOOK_PATH_TIMEWEB
    url_db = SqlUrlService.urls_base
    username_support = BotParams.username_support
    redis_url = RedisBD.PROD_REDIS

url_support = f"https//t.me/{username_support}"
currently_msk = DateTemplate().conclusion_date(option="time_now").replace(tzinfo=None)
