"""API routes"""
from app.routes.video import router as video_router
from app.routes.roi import router as roi_router
from app.routes.health import router as health_router

__all__ = ["video_router", "roi_router", "health_router"]
