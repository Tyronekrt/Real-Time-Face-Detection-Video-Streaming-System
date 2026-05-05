"""Tests for ROI endpoints"""
import pytest
from app.schemas.roi import ROICreateSchema
from app.services.roi_service import ROIService
from tests.conftest import client


def test_create_roi(test_session):
    """Test creating a ROI record"""
    roi_data = ROICreateSchema(
        frame_number=1,
        x_min=10.0,
        y_min=20.0,
        x_max=100.0,
        y_max=200.0,
        confidence=0.95,
        video_session_id="test-session"
    )
    
    roi = ROIService.create_roi(test_session, roi_data)
    
    assert roi.id is not None
    assert roi.frame_number == 1
    assert roi.x_min == 10.0
    assert roi.confidence == 0.95


def test_get_roi_by_id(test_session):
    """Test getting ROI by ID"""
    # Create a ROI first
    roi_data = ROICreateSchema(
        frame_number=1,
        x_min=10.0,
        y_min=20.0,
        x_max=100.0,
        y_max=200.0,
        confidence=0.95,
    )
    
    roi = ROIService.create_roi(test_session, roi_data)
    
    # Retrieve it
    retrieved = ROIService.get_roi_by_id(test_session, roi.id)
    
    assert retrieved is not None
    assert retrieved.id == roi.id
    assert retrieved.frame_number == 1


def test_get_roi_by_frame(test_session):
    """Test getting ROI by frame number"""
    roi_data = ROICreateSchema(
        frame_number=42,
        x_min=10.0,
        y_min=20.0,
        x_max=100.0,
        y_max=200.0,
        confidence=0.95,
    )
    
    roi = ROIService.create_roi(test_session, roi_data)
    
    retrieved = ROIService.get_roi_by_frame(test_session, 42)
    
    assert retrieved is not None
    assert retrieved.frame_number == 42


def test_get_all_rois(test_session):
    """Test getting all ROIs"""
    # Create multiple ROIs
    for i in range(3):
        roi_data = ROICreateSchema(
            frame_number=i,
            x_min=10.0 + i,
            y_min=20.0,
            x_max=100.0,
            y_max=200.0,
            confidence=0.95,
            video_session_id="test-session"
        )
        ROIService.create_roi(test_session, roi_data)
    
    rois = ROIService.get_all_rois(test_session, video_session_id="test-session")
    
    assert len(rois) == 3


def test_delete_roi(test_session):
    """Test deleting a ROI"""
    roi_data = ROICreateSchema(
        frame_number=1,
        x_min=10.0,
        y_min=20.0,
        x_max=100.0,
        y_max=200.0,
        confidence=0.95,
    )
    
    roi = ROIService.create_roi(test_session, roi_data)
    roi_id = roi.id
    
    # Delete it
    success = ROIService.delete_roi(test_session, roi_id)
    
    assert success is True
    
    # Verify it's gone
    retrieved = ROIService.get_roi_by_id(test_session, roi_id)
    assert retrieved is None
