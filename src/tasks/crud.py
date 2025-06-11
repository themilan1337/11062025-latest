from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from ..database import User, TaskDB
from ..auth import get_password_hash
from .models import UserCreate, TaskCreate, TaskUpdate


class UserCRUD:
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Create a new user."""
        try:
            hashed_password = get_password_hash(user.password)
            db_user = User(
                username=user.username,
                email=user.email,
                hashed_password=hashed_password
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()


class TaskCRUD:
    @staticmethod
    def create_task(db: Session, task: TaskCreate, user_id: int) -> TaskDB:
        """Create a new task for a user."""
        db_task = TaskDB(**task.dict(), owner_id=user_id)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def get_tasks_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[TaskDB]:
        """Get all tasks for a specific user."""
        return db.query(TaskDB).filter(TaskDB.owner_id == user_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_task_by_id(db: Session, task_id: int, user_id: int) -> Optional[TaskDB]:
        """Get a specific task by ID for a user."""
        return db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.owner_id == user_id).first()
    
    @staticmethod
    def update_task(db: Session, task_id: int, task_update: TaskUpdate, user_id: int) -> Optional[TaskDB]:
        """Update a task."""
        db_task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.owner_id == user_id).first()
        if not db_task:
            return None
        
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def delete_task(db: Session, task_id: int, user_id: int) -> bool:
        """Delete a task."""
        db_task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.owner_id == user_id).first()
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        return True
