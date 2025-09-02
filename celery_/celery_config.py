from settings import LOCAL_REDIS

broker_url = LOCAL_REDIS
result_backend = LOCAL_REDIS

task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'Europe/Moscow'
enable_utc = True

# celery -A celery_.celery_app worker -l info -P solo
# celery -A celery_.celery_app beat -l info

worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000
worker_max_memory_per_child = 150000

path_tasks = 'celery_.tasks.'
beat_schedule = {
    "notify-expiring-subscriptions": {
        'task': path_tasks + 'notify_expiring_subscriptions',
        'schedule': 43200.0,
    }
}
