"""Tests for face detection service"""
import pytest
import numpy as np
from app.services.face_detector import FaceDetectorService, BoundingBox


def test_bounding_box_creation():
    """Test BoundingBox class"""
    bbox = BoundingBox(10, 20, 100, 200)
    
    assert bbox.x_min == 10
    assert bbox.y_min == 20
    assert bbox.x_max == 100
    assert bbox.y_max == 200
    assert bbox.width == 90
    assert bbox.height == 180


def test_bounding_box_to_dict():
    """Test BoundingBox to_dict method"""
    bbox = BoundingBox(10, 20, 100, 200)
    bbox_dict = bbox.to_dict()
    
    assert bbox_dict["x_min"] == 10
    assert bbox_dict["width"] == 90
    assert bbox_dict["height"] == 180


def test_face_detector_initialization():
    """Test FaceDetectorService initialization"""
    detector = FaceDetectorService(confidence_threshold=0.5)
    
    assert detector.confidence_threshold == 0.5
    assert detector.detector is not None


def test_detect_faces_on_empty_frame():
    """Test detect_faces with empty frame"""
    detector = FaceDetectorService()
    
    # Empty frame
    empty_frame = np.array([], dtype=np.uint8)
    boxes, confidences = detector.detect_faces(empty_frame)
    
    assert boxes == []
    assert confidences == []


def test_detect_faces_on_random_frame():
    """Test detect_faces on random frame (no face)"""
    detector = FaceDetectorService()
    
    # Random frame without face
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    boxes, confidences = detector.detect_faces(frame)
    
    # Random frame should not cause errors
    assert isinstance(boxes, list)
    assert isinstance(confidences, list)


def test_get_dominant_face_on_no_face():
    """Test get_dominant_face when no face detected"""
    detector = FaceDetectorService()
    
    # Random frame
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    result = detector.get_dominant_face(frame)
    
    # Should return None when no face detected
    assert result is None or (result[0] is None)


def test_draw_roi_on_frame():
    """Test drawing ROI on frame"""
    detector = FaceDetectorService()
    
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    bbox = BoundingBox(100, 100, 300, 300)
    
    output_frame = detector.draw_roi_on_frame(frame, bbox, color=(0, 255, 0), thickness=2)
    
    # Check that the original frame is not modified
    assert np.array_equal(frame, np.zeros((480, 640, 3), dtype=np.uint8))
    
    # Check that output frame has changes (rectangle drawn)
    assert not np.array_equal(frame, output_frame)


def test_draw_roi_color():
    """Test drawing ROI with different colors"""
    detector = FaceDetectorService()
    
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    bbox = BoundingBox(100, 100, 300, 300)
    
    # Red rectangle
    red_frame = detector.draw_roi_on_frame(frame.copy(), bbox, color=(255, 0, 0), thickness=2)
    assert not np.array_equal(frame, red_frame)
    
    # Green rectangle
    green_frame = detector.draw_roi_on_frame(frame.copy(), bbox, color=(0, 255, 0), thickness=2)
    assert not np.array_equal(frame, green_frame)
