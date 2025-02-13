import os
from celery import Celery

# Celery configuration
BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")
REDIS_URL = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery = Celery(
    "moderation_tasks",
    broker=BROKER_URL,
    backend=REDIS_URL,
    include=["app.tasks.moderation"]
)

# Celery configurations
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_acks_late=True,  # Ensure tasks are not lost if workers fail
    worker_prefetch_multiplier=1,  # Prevent task starvation
    broker_connection_retry_on_startup=True,  # Retry connection on startup
    task_track_started=True,  # Track when tasks are started
    task_time_limit=300,  # 5 minute timeout for tasks
    task_soft_time_limit=240,  # Soft timeout 4 minutes
)

# Route tasks to specific queues
celery.conf.task_routes = {
    "app.tasks.moderation.moderate_text_task": {"queue": "moderation_queue"},
}

# Queue definitions
celery.conf.task_queues = {
    "moderation_queue": {
        "exchange": "moderation",
        "routing_key": "moderation",
    },
    "dead_letter_queue": {
        "exchange": "dead_letter",
        "routing_key": "dead_letter",
    }
}

celery.conf.task_default_queue = "moderation_queue"