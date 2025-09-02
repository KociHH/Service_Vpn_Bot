from utils.other import redis_url
from celery import Celery
from settings import *

celery_app = Celery(
    'shadevpn',
    broker=redis_url,
    backend=redis_url,
    include=['celery_.tasks']
)

celery_app.config_from_object('celery_.celery_config') 

