import aiohttp
import os
import json
import random
import uuid
import redis
import asyncio
from celery import shared_task
from app.config.db import AsyncSessionLocal
from app.models.moderation import ModerationResult
from sqlalchemy.orm import Session
from app.config.db import SyncSessionLocal

# Redis setup for caching
redis_client = redis.Redis(host="redis", port=6379, db=0)

OPENAI_MODERATION_URL = "https://api.openai.com/v1/moderations"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")

async def get_mock_moderation_response(text: str):
    """
    Generates a mock response similar to OpenAI's Moderation API.
    """
    categories = {
        "sexual": random.choice([True, False]),
        "hate": random.choice([True, False]),
        "harassment": random.choice([True, False]),
        "self-harm": random.choice([True, False]),
        "sexual/minors": random.choice([True, False]),
        "hate/threatening": random.choice([True, False]),
        "violence/graphic": random.choice([True, False]),
        "self-harm/intent": random.choice([True, False]),
        "self-harm/instructions": random.choice([True, False]),
        "harassment/threatening": random.choice([True, False]),
        "violence": random.choice([True, False]),
    }
    category_scores = {key: random.uniform(0.0, 1.0) for key in categories}
    return {
        "id": f"modr-{uuid.uuid4().hex}",
        "model": "text-moderation-mock",
        "results": [
            {
                "flagged": any(categories.values()),
                "categories": categories,
                "category_scores": category_scores,
            }
        ]
    }

async def fetch_moderation(text: str):
    """
    Calls OpenAI Moderation API to analyze the text.
    """
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"input": text}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(OPENAI_MODERATION_URL, headers=headers, json=data) as response:
            if response.status != 200:
                return await get_mock_moderation_response(text)  # Fallback to mock
            return await response.json()

def run_async(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

def run_async_function(coroutine):
    """
    Helper function to run async functions in a synchronous context.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coroutine)
    finally:
        loop.close()

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def moderate_text_task(self, text: str):
    """
    Celery task to process moderation. Falls back to mock response if needed.
    """
    # Check if cached result exists
    cached_result = redis_client.get(text)
    if cached_result:
        return json.loads(cached_result)
    
    # Fetch moderation result
    try:
        moderation_result = run_async_function(fetch_moderation(text))
    except Exception:
        moderation_result = run_async_function(get_mock_moderation_response(text))
    
    flagged = moderation_result["results"][0]["flagged"]
    category = ",".join([key for key, value in moderation_result["results"][0]["categories"].items() if value])
    
    # Use a synchronous database session
    session = SyncSessionLocal()
    try:
        moderation_entry = ModerationResult(
            content=text, 
            flagged=flagged, 
            category=category
        )
        session.add(moderation_entry)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    
    # Cache result in Redis for 1 hour
    redis_client.setex(text, 3600, json.dumps(moderation_result))
    
    return moderation_result
