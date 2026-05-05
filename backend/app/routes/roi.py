"""ROI data endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.roi_service import ROIService
from app.schemas.roi import ROISchema, ROIListResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/roi", tags=["roi"])


@router.get("/{roi_id}", response_model=ROISchema)
async def get_roi(roi_id: int, db: Session = Depends(get_db)):
    """
    Get a specific ROI by ID
    
    Returns the bounding box coordinates and metadata for a detected face region
    """
    roi = ROIService.get_roi_by_id(db, roi_id)
    
    if not roi:
        raise HTTPException(status_code=404, detail="ROI not found")
    
    return roi


@router.get("/frame/{frame_number}", response_model=Optional[ROISchema])
async def get_roi_by_frame(frame_number: int, db: Session = Depends(get_db)):
    """
    Get ROI data for a specific frame number
    
    Useful for looking up face data by frame number
    """
    roi = ROIService.get_roi_by_frame(db, frame_number)
    
    if not roi:
        raise HTTPException(status_code=404, detail="ROI not found for frame")
    
    return roi


@router.get("/session/{session_id}", response_model=ROIListResponse)
async def get_session_rois(
    session_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    Get all ROI data for a specific video session
    
    Returns paginated list of detected faces for a video session
    """
    rois = ROIService.get_all_rois(db, skip=skip, limit=limit, video_session_id=session_id)
    
    return {
        "total": len(rois),
        "rois": rois,
    }


@router.get("/", response_model=ROIListResponse)
async def get_all_rois(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    video_session_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get all ROI data (paginated)
    
    Optional filter by video_session_id
    """
    rois = ROIService.get_all_rois(
        db,
        skip=skip,
        limit=limit,
        video_session_id=video_session_id,
    )
    
    return {
        "total": len(rois),
        "rois": rois,
    }


@router.get("/latest/{session_id}", response_model=Optional[ROISchema])
async def get_latest_roi(session_id: str, db: Session = Depends(get_db)):
    """
    Get the latest (most recent) ROI for a video session
    
    Useful for real-time updates
    """
    roi = ROIService.get_latest_roi(db, video_session_id=session_id)
    
    if not roi:
        raise HTTPException(status_code=404, detail="No ROI found for session")
    
    return roi


@router.delete("/{roi_id}")
async def delete_roi(roi_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific ROI record
    """
    success = ROIService.delete_roi(db, roi_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="ROI not found")
    
    return {
        "status": "success",
        "message": f"ROI {roi_id} deleted successfully",
    }
