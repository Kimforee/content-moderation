from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.db import get_db
from app.services.moderation import moderate_text
from pydantic import BaseModel

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
    API endpoint to moderate text using OpenAI's Moderation API.
    """
    result = await moderate_text(request.content, db)  # Read content from request body
    return result