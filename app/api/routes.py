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

router = APIRouter()

class TextRequest(BaseModel):
    content: str

@router.get("/")
async def root():
    """
    Root endpoint.
    """
    return {"message": "Welcome to the Content Moderation API"}

@router.post("/api/v1/moderate/text")
async def moderate_text_api(request: TextRequest, db: AsyncSession = Depends(get_db)):
    """
    API endpoint to trigger moderation task.
    Returns task_id immediately but waits briefly for results.
    """
    task = moderate_text_task.delay(request.content)

    # Wait up to 5 seconds for completion
    for _ in range(10):  
        result = AsyncResult(task.id)
        if result.ready():
            return {"task_id": task.id, "status": "completed", "result": result.result}
        sleep(0.5)  # Wait 0.5 seconds before checking again

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