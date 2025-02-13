from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.db import get_db_session as get_db
from app.services.moderation import moderate_text
from app.tasks.moderation import moderate_text_task
from celery.result import AsyncResult
from app.config.celery import celery 
from pydantic import BaseModel
from time import sleep
from celery import Celery
import time
from starlette.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.config.metrics import record_request
from app.config.logging import log_info, log_error

router = APIRouter()

class TextRequest(BaseModel):
    content: str

@router.get("/")
async def root():
    """
    Root endpoint.
    """
    return {"message": "Welcome to the Content Moderation API"}

@router.get("/metrics")
async def metrics():
    """ Exposes Prometheus metrics """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.post("/api/v1/moderate/text")
async def moderate_text_api(request: TextRequest, db: AsyncSession = Depends(get_db)):
    """
    API endpoint to trigger moderation task.
    Returns task_id immediately but waits briefly for results.
    """
    start_time = time.time()
    task = moderate_text_task.delay(request.content)
    log_info("Received moderation request", content=request.content)
    
    # Wait up to 5 seconds for completion
    for _ in range(10):  
        result = AsyncResult(task.id)
        if result.ready():
            response = {"task_id": task.id, "status": "completed", "result": result.result}
            latency = time.time() - start_time
            record_request("/api/v1/moderate/text", "POST", latency)
            log_info("Moderation task started", task_id=task.id)
            return response
        sleep(0.5)  # Wait 0.5 seconds before checking again

    latency = time.time() - start_time
    record_request("/api/v1/moderate/text", "POST", latency)
    log_info("Moderation task started", task_id=task.id)
    # If still processing, return task_id so user can check later
    return {"task_id": task.id, "status": "processing"}

@router.get("/api/v1/moderate/status/{task_id}")
async def get_task_status(task_id: str):
    """
    API endpoint to check the status of a moderation task.
    """
    task = AsyncResult(task_id, app=celery)  # Use the imported celery instance
    if task.state == "FAILURE":
        raise HTTPException(status_code=500, detail="Task failed")
    return {
        "task_id": task_id,
        "status": task.state,
        "result": task.result if task.ready() else None
    }