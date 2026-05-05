"""Face detection service using MediaPipe without OpenCV"""
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


class BoundingBox:
    """Axis-aligned minimal bounding box (AAMBB) for face ROI"""
    
    def __init__(self, x_min: float, y_min: float, x_max: float, y_max: float):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.width = x_max - x_min
        self.height = y_max - y_min
        
    def to_dict(self) -> dict:
        """Convert bounding box to dictionary"""
        return {
            "x_min": self.x_min,
            "y_min": self.y_min,
            "x_max": self.x_max,
            "y_max": self.y_max,
            "width": self.width,
            "height": self.height,
        }


class FaceDetectorService:
    """Service for detecting faces in video frames using MediaPipe"""
    
    def __init__(self, confidence_threshold: float = 0.5):
        """Initialize face detector
        
        Args:
            confidence_threshold: Minimum confidence score for detection
        """
        self.confidence_threshold = confidence_threshold
        
        # Initialize MediaPipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.detector = self.mp_face_detection.FaceDetection(
            model_selection=0,  # 0 for short-range, 1 for full-range
            min_detection_confidence=confidence_threshold,
        )
        
        logger.info(
            f"Face detector initialized with threshold: {confidence_threshold}"
        )
    
    def detect_faces(
        self, frame: np.ndarray
    ) -> Tuple[List[BoundingBox], List[float]]:
        """Detect faces in a frame
        
        Args:
            frame: Input RGB frame as numpy array (H, W, 3)
            
        Returns:
            Tuple of (list of BoundingBox objects, list of confidence scores)
        """
        if frame is None or frame.size == 0:
            return [], []
        
        try:
            # Convert BGR to RGB if needed (assuming OpenCV format input)
            # MediaPipe expects RGB format
            results = self.detector.process(frame)
            
            boxes = []
            confidences = []
            
            if results.detections:
                h, w, _ = frame.shape
                
                for detection in results.detections:
                    # Get bounding box coordinates (normalized 0-1)
                    bbox = detection.location_data.relative_bounding_box
                    
                    # Convert normalized coordinates to pixel coordinates
                    x_min = max(0, int(bbox.xmin * w))
                    y_min = max(0, int(bbox.ymin * h))
                    x_max = min(w, int((bbox.xmin + bbox.width) * w))
                    y_max = min(h, int((bbox.ymin + bbox.height) * h))
                    
                    # Get confidence score
                    confidence = detection.score[0] if detection.score else 0.0
                    
                    # Create bounding box
                    box = BoundingBox(x_min, y_min, x_max, y_max)
                    boxes.append(box)
                    confidences.append(confidence)
            
            return boxes, confidences
            
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return [], []
    
    def get_dominant_face(
        self, frame: np.ndarray
    ) -> Optional[Tuple[BoundingBox, float]]:
        """Get the largest/most confident face from frame
        
        Assumes only one face will be present.
        
        Args:
            frame: Input RGB frame
            
        Returns:
            Tuple of (BoundingBox, confidence) or None if no face detected
        """
        boxes, confidences = self.detect_faces(frame)
        
        if not boxes:
            return None
        
        # Return the face with highest confidence (assumes single face)
        if len(boxes) == 1:
            return boxes[0], confidences[0]
        
        # If multiple faces detected, get the largest one
        max_idx = max(range(len(boxes)), key=lambda i: boxes[i].width * boxes[i].height)
        return boxes[max_idx], confidences[max_idx]
    
    def draw_roi_on_frame(
        self,
        frame: np.ndarray,
        bbox: BoundingBox,
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2,
    ) -> np.ndarray:
        """Draw ROI rectangle on frame without using OpenCV
        
        Args:
            frame: Input frame as numpy array
            bbox: Bounding box to draw
            color: RGB color tuple
            thickness: Line thickness in pixels
            
        Returns:
            Frame with drawn bounding box
        """
        # Create a copy to avoid modifying original
        output_frame = frame.copy()
        
        # Convert pixel coordinates to integers
        x_min, y_min = int(bbox.x_min), int(bbox.y_min)
        x_max, y_max = int(bbox.x_max), int(bbox.y_max)
        
        # Draw rectangle by setting pixels (since we can't use OpenCV)
        # Top horizontal line
        output_frame[y_min:y_min+thickness, x_min:x_max] = color
        
        # Bottom horizontal line
        output_frame[y_max-thickness:y_max, x_min:x_max] = color
        
        # Left vertical line
        output_frame[y_min:y_max, x_min:x_min+thickness] = color
        
        # Right vertical line
        output_frame[y_min:y_max, x_max-thickness:x_max] = color
        
        return output_frame
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'detector'):
            self.detector.close()
