"""ROI Pydantic schemas"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ROICreateSchema(BaseModel):
    """Schema for creating ROI entries"""
    
    frame_number: int
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    confidence: float
    video_session_id: Optional[str] = None


class ROISchema(ROICreateSchema):
    """Complete ROI schema with database ID"""
    
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ROIListResponse(BaseModel):
    """Response for listing ROIs"""
    
    total: int
    rois: list[ROISchema]
