"""ROI (Region of Interest) database model"""
from sqlalchemy import Column, Integer, Float, DateTime, String
from sqlalchemy.sql import func
from app.database import Base


class ROI(Base):
    """Region of Interest data for detected faces"""
    
    __tablename__ = "rois"
    
    id = Column(Integer, primary_key=True, index=True)
    frame_number = Column(Integer, nullable=False)
    x_min = Column(Float, nullable=False, comment="Left edge of bounding box")
    y_min = Column(Float, nullable=False, comment="Top edge of bounding box")
    x_max = Column(Float, nullable=False, comment="Right edge of bounding box")
    y_max = Column(Float, nullable=False, comment="Bottom edge of bounding box")
    confidence = Column(Float, nullable=False, comment="Detection confidence score")
    video_session_id = Column(String(50), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    def __repr__(self):
        """String representation of ROI"""
        return (
            f"<ROI(id={self.id}, frame={self.frame_number}, "
            f"box=({self.x_min}, {self.y_min}, {self.x_max}, {self.y_max}))>"
        )


class VideoFrame(Base):
    """Video frame metadata for tracking"""
    
    __tablename__ = "video_frames"
    
    id = Column(Integer, primary_key=True, index=True)
    frame_number = Column(Integer, nullable=False, index=True)
    video_session_id = Column(String(50), nullable=True, index=True)
    frame_timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
