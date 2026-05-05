"""Health check endpoints"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Face Detection Video Streaming API",
        "version": "1.0.0",
    }
