from celery import current_app as celery_app
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database import get_db, TaskDB
from src.config import settings
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def cleanup_old_tasks(self):
    """
    Clean up completed tasks older than 30 days
    """
    try:
        db = next(get_db())
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Delete old completed tasks
        deleted_count = db.query(TaskDB).filter(
            TaskDB.completed == True,
            TaskDB.updated_at < cutoff_date
        ).delete()
        
        db.commit()
        logger.info(f"Cleaned up {deleted_count} old completed tasks")
        return {"deleted_count": deleted_count, "status": "success"}
        
    except Exception as exc:
        logger.error(f"Error cleaning up old tasks: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)
    finally:
        db.close()

@celery_app.task(bind=True)
def send_task_reminder(self, task_id: int, user_email: str):
    """
    Send reminder for upcoming task deadline
    """
    try:
        # This would integrate with an email service
        # For now, just log the reminder
        logger.info(f"Reminder: Task {task_id} deadline approaching for {user_email}")
        return {"task_id": task_id, "user_email": user_email, "status": "reminder_sent"}
        
    except Exception as exc:
        logger.error(f"Error sending task reminder: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@celery_app.task(bind=True)
def process_bulk_tasks(self, task_data_list: list):
    """
    Process multiple tasks in bulk
    """
    try:
        db = next(get_db())
        processed_count = 0
        
        for task_data in task_data_list:
            # Process each task
            # This is a placeholder for bulk task processing logic
            processed_count += 1
            
        logger.info(f"Processed {processed_count} tasks in bulk")
        return {"processed_count": processed_count, "status": "success"}
        
    except Exception as exc:
        logger.error(f"Error processing bulk tasks: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)
    finally:
        db.close()