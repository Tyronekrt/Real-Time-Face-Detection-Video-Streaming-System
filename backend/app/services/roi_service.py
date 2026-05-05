"""ROI service for database operations"""
from sqlalchemy.orm import Session
from app.models.roi import ROI
from app.schemas.roi import ROICreateSchema
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class ROIService:
    """Service for managing ROI data in the database"""
    
    @staticmethod
    def create_roi(db: Session, roi_data: ROICreateSchema) -> ROI:
        """Create a new ROI record
        
        Args:
            db: Database session
            roi_data: ROI data to create
            
        Returns:
            Created ROI object
        """
        try:
            db_roi = ROI(**roi_data.model_dump())
            db.add(db_roi)
            db.commit()
            db.refresh(db_roi)
            logger.info(f"Created ROI record: {db_roi}")
            return db_roi
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating ROI: {e}")
            raise
    
    @staticmethod
    def get_roi_by_id(db: Session, roi_id: int) -> Optional[ROI]:
        """Get ROI by ID
        
        Args:
            db: Database session
            roi_id: ROI ID
            
        Returns:
            ROI object or None
        """
        return db.query(ROI).filter(ROI.id == roi_id).first()
    
    @staticmethod
    def get_roi_by_frame(db: Session, frame_number: int) -> Optional[ROI]:
        """Get ROI for a specific frame
        
        Args:
            db: Database session
            frame_number: Frame number
            
        Returns:
            ROI object or None
        """
        return db.query(ROI).filter(ROI.frame_number == frame_number).first()
    
    @staticmethod
    def get_all_rois(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        video_session_id: Optional[str] = None,
    ) -> List[ROI]:
        """Get all ROI records with optional filtering
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            video_session_id: Optional filter by video session
            
        Returns:
            List of ROI objects
        """
        query = db.query(ROI)
        
        if video_session_id:
            query = query.filter(ROI.video_session_id == video_session_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_latest_roi(db: Session, video_session_id: Optional[str] = None) -> Optional[ROI]:
        """Get the latest ROI record
        
        Args:
            db: Database session
            video_session_id: Optional filter by video session
            
        Returns:
            Latest ROI object or None
        """
        query = db.query(ROI)
        
        if video_session_id:
            query = query.filter(ROI.video_session_id == video_session_id)
        
        return query.order_by(ROI.frame_number.desc()).first()
    
    @staticmethod
    def delete_roi(db: Session, roi_id: int) -> bool:
        """Delete a ROI record
        
        Args:
            db: Database session
            roi_id: ROI ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            roi = db.query(ROI).filter(ROI.id == roi_id).first()
            if roi:
                db.delete(roi)
                db.commit()
                logger.info(f"Deleted ROI: {roi_id}")
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting ROI: {e}")
            raise
