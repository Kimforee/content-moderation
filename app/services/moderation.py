import aiohttp
import os
import json
import random
import uuid
import redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.moderation import ModerationResult

# Redis setup for caching
# redis_client = redis.Redis(host="localhost", port=6379, db=0)
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


async def moderate_text(text: str, db: AsyncSession):
    """
    Sends text content to OpenAI's moderation API.
    If API fails, it falls back to a mock moderation response.
    Stores results in PostgreSQL and caches them in Redis.
    """

    # Check if result is cached
    cached_result = redis_client.get(text)
    if cached_result:
        return json.loads(cached_result)

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {"input": text}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OPENAI_MODERATION_URL, headers=headers, json=data) as response:
                if response.status != 200:
                    raise Exception("Failed to reach OpenAI API")

                result = await response.json()
    except Exception:
        result = await get_mock_moderation_response(text)

    flagged = result["results"][0]["flagged"]
    category = ",".join([key for key, value in result["results"][0]["categories"].items() if value])

    # Store in the database
    moderation_entry = ModerationResult(content=text, flagged=flagged, category=category)
    db.add(moderation_entry)
    await db.commit()

    # Cache result in Redis
    redis_client.setex(text, 3600, json.dumps(result))  # Cache for 1 hour

    return result
