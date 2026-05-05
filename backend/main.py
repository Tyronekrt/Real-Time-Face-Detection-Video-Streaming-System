"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
import logging

from app.config import settings
from app.database import init_db
from app.routes import health_router, video_router, roi_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZIP compression middleware
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# Initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


# Include routers
app.include_router(health_router)
app.include_router(video_router)
app.include_router(roi_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Face Detection Video Streaming API",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "endpoints": {
            "health": "/api/health/",
            "video": {
                "upload": "POST /api/video/upload",
                "stream": "GET /api/video/stream/{session_id}",
                "websocket": "WS /api/video/ws/{session_id}",
                "process_frame": "POST /api/video/process-frame",
            },
            "roi": {
                "get_roi": "GET /api/roi/{roi_id}",
                "get_by_frame": "GET /api/roi/frame/{frame_number}",
                "get_session_rois": "GET /api/roi/session/{session_id}",
                "get_all": "GET /api/roi/",
                "get_latest": "GET /api/roi/latest/{session_id}",
                "delete": "DELETE /api/roi/{roi_id}",
            },
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
