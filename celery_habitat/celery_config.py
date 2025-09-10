from utils.work import redis_url

broker_url = redis_url
result_backend = redis_url

task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'Europe/Moscow'
enable_utc = True

# celery -A celery_habitat.celery_app worker -l info -P solo
# celery -A celery_habitat.celery_app beat -l info

worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000
worker_max_memory_per_child = 150000

path_tasks = 'celery_habitat.tasks.'
beat_schedule = {
    "notify-expiring-subscriptions": {
        'task': path_tasks + 'notify_expiring_subscriptions',
        'schedule': 21600.0, # 6ч
    }
}
