from fastapi import FastAPI
from app.api.routes import router
import os

app = FastAPI(title="Content Moderation API", version="1.0")

# Include API routes
app.include_router(router)

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to ensure service is running.
    """
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
