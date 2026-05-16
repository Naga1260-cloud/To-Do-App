import logging
import time
import uuid
from datetime import date
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from pythonjsonlogger import jsonlogger
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator

import crud
import schemas
from database import get_db

# ── Structured JSON Logger Setup ──────────────────────────────────────────────
logger = logging.getLogger("todo_api")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Also configure uvicorn loggers to JSON
for uvicorn_logger in ("uvicorn", "uvicorn.access", "uvicorn.error"):
    uv_logger = logging.getLogger(uvicorn_logger)
    uv_logger.handlers = []
    uv_logger.addHandler(handler)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Todo API", version="1.0.0")

Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request Logging Middleware ────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.time()

    logger.info(
        "request_started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
        },
    )

    response: Response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 2)

    level = logging.WARNING if response.status_code >= 400 else logging.INFO
    logger.log(
        level,
        "request_completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )

    response.headers["X-Request-ID"] = request_id
    return response

# ── Startup / Shutdown ────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("application_started", extra={"version": "1.0.0", "port": 8000})

@app.on_event("shutdown")
async def shutdown():
    logger.info("application_stopped")

# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    from database import engine
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "up"}
    except Exception as e:
        logger.error("health_check_db_failed", extra={"error": str(e)})
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "database": "down", "detail": str(e)},
        )

# ── Todo Routes ───────────────────────────────────────────────────────────────
@app.get("/todos", response_model=List[schemas.TodoResponse])
def list_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    todos = crud.get_todos(db, skip=skip, limit=limit)
    logger.info("todos_listed", extra={"count": len(todos), "skip": skip, "limit": limit})
    return todos

@app.get("/todos/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = crud.get_todo(db, todo_id)
    if not todo:
        logger.warning("todo_not_found", extra={"todo_id": todo_id})
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.post("/todos", response_model=schemas.TodoResponse, status_code=201)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    created = crud.create_todo(db, todo)
    logger.info("todo_created", extra={"todo_id": created.id, "title": created.title, "priority": created.priority})
    return created

@app.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, todo_update: schemas.TodoUpdate, db: Session = Depends(get_db)):
    todo = crud.update_todo(db, todo_id, todo_update)
    if not todo:
        logger.warning("todo_not_found_for_update", extra={"todo_id": todo_id})
        raise HTTPException(status_code=404, detail="Todo not found")
    logger.info("todo_updated", extra={"todo_id": todo_id})
    return todo

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    success = crud.delete_todo(db, todo_id)
    if not success:
        logger.warning("todo_not_found_for_delete", extra={"todo_id": todo_id})
        raise HTTPException(status_code=404, detail="Todo not found")
    logger.info("todo_deleted", extra={"todo_id": todo_id})

@app.patch("/todos/{todo_id}/complete", response_model=schemas.TodoResponse)
def mark_complete(todo_id: int, db: Session = Depends(get_db)):
    update = schemas.TodoUpdate(is_completed=True, completed_date=date.today())
    todo = crud.update_todo(db, todo_id, update)
    if not todo:
        logger.warning("todo_not_found_for_complete", extra={"todo_id": todo_id})
        raise HTTPException(status_code=404, detail="Todo not found")
    logger.info("todo_marked_complete", extra={"todo_id": todo_id, "completed_date": str(date.today())})
    return todo

@app.patch("/todos/{todo_id}/incomplete", response_model=schemas.TodoResponse)
def mark_incomplete(todo_id: int, db: Session = Depends(get_db)):
    update = schemas.TodoUpdate(is_completed=False, completed_date=None)
    todo = crud.update_todo(db, todo_id, update)
    if not todo:
        logger.warning("todo_not_found_for_incomplete", extra={"todo_id": todo_id})
        raise HTTPException(status_code=404, detail="Todo not found")
    logger.info("todo_marked_incomplete", extra={"todo_id": todo_id})
    return todo

