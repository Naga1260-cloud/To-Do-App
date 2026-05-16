import logging
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
import models
import schemas

logger = logging.getLogger("todo_api.crud")

def get_todos(db: Session, skip: int = 0, limit: int = 100) -> List[models.Todo]:
    return db.query(models.Todo).order_by(desc(models.Todo.created_at)).offset(skip).limit(limit).all()

def get_todo(db: Session, todo_id: int) -> Optional[models.Todo]:
    return db.query(models.Todo).filter(models.Todo.id == todo_id).first()

def create_todo(db: Session, todo: schemas.TodoCreate) -> models.Todo:
    db_todo = models.Todo(
        title=todo.title,
        description=todo.description,
        due_date=todo.due_date,
        priority=todo.priority,
        is_completed=False,
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    logger.debug("db_todo_created", extra={"todo_id": db_todo.id})
    return db_todo

def update_todo(db: Session, todo_id: int, todo_update: schemas.TodoUpdate) -> Optional[models.Todo]:
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return None
    update_data = todo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_todo, field, value)
    db.commit()
    db.refresh(db_todo)
    logger.debug("db_todo_updated", extra={"todo_id": todo_id, "fields": list(update_data.keys())})
    return db_todo

def delete_todo(db: Session, todo_id: int) -> bool:
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return False
    db.delete(db_todo)
    db.commit()
    logger.debug("db_todo_deleted", extra={"todo_id": todo_id})
    return True

