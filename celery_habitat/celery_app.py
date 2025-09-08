from utils.work import redis_url
from celery import Celery
from settings import *

celery_app = Celery(
    'shadevpn',
    broker=redis_url,
    backend=redis_url,
    include=['celery_habitat.tasks']
)

celery_app.config_from_object("celery_habitat.celery_config") 

