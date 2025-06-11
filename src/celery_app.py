from celery import Celery
from celery.schedules import crontab
from src.config import settings

# Create Celery instance
celery_app = Celery(
    "task_management",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "src.tasks.celery_tasks",
        "src.scraper.tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks configuration
celery_app.conf.beat_schedule = {
    "scrape-data-daily": {
        "task": "src.scraper.tasks.scrape_website_data",
        "schedule": crontab(hour=0, minute=0),  # Run daily at midnight
    },
    "cleanup-old-tasks": {
        "task": "src.tasks.celery_tasks.cleanup_old_tasks",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
}

if __name__ == "__main__":
    celery_app.start()