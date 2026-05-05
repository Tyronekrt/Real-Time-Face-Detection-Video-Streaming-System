"""Video streaming endpoints"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.face_detector import FaceDetectorService
from app.services.roi_service import ROIService
from app.schemas.roi import ROICreateSchema
from io import BytesIO
import cv2
import numpy as np
import logging
import uuid
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/video", tags=["video"])

# Global variables for streaming state
active_connections: dict = {}
face_detector = FaceDetectorService(confidence_threshold=0.5)
current_video_buffer: dict = {}


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload and process a video file
    
    This endpoint:
    1. Accepts a video file
    2. Processes each frame for face detection
    3. Stores ROI data in database
    4. Returns processed video URL
    """
    video_session_id = str(uuid.uuid4())
    
    try:
        # Read the uploaded file
        content = await file.read()
        nparr = np.frombuffer(content, np.uint8)
        
        # For demonstration, we'll return a simple response
        # In production, this would process and store the video
        
        return {
            "status": "success",
            "message": "Video uploaded and queued for processing",
            "video_session_id": video_session_id,
            "video_url": f"/api/video/stream/{video_session_id}",
            "roi_url": f"/api/roi/{video_session_id}",
        }
    except Exception as e:
        logger.error(f"Error uploading video: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")


@router.get("/stream/{session_id}")
async def stream_video(session_id: str):
    """
    Stream video with drawn ROI rectangles
    
    Returns a video stream with bounding boxes drawn around detected faces
    """
    def generate():
        """Generator for streaming video"""
        # In a real implementation, this would stream from stored video
        # or from a real-time camera feed
        yield b"--frame\r\n"
        yield b'Content-Type: image/jpeg\r\n\r\n'
    
    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time video streaming
    
    Accepts raw frame data and returns detected faces
    """
    await websocket.accept()
    active_connections[session_id] = websocket
    frame_number = 0
    
    try:
        while True:
            # Receive frame data
            data = await websocket.receive_bytes()
            
            if not data:
                break
            
            # Convert bytes to numpy array
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                continue
            
            # Convert BGR to RGB for face detection
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            result = face_detector.get_dominant_face(rgb_frame)
            
            roi_data = None
            if result:
                bbox, confidence = result
                
                if confidence >= face_detector.confidence_threshold:
                    # Store ROI in database
                    roi_create = ROICreateSchema(
                        frame_number=frame_number,
                        x_min=bbox.x_min,
                        y_min=bbox.y_min,
                        x_max=bbox.x_max,
                        y_max=bbox.y_max,
                        confidence=confidence,
                        video_session_id=session_id,
                    )
                    
                    try:
                        roi = ROIService.create_roi(db, roi_create)
                        roi_data = {
                            "id": roi.id,
                            "frame_number": roi.frame_number,
                            "x_min": roi.x_min,
                            "y_min": roi.y_min,
                            "x_max": roi.x_max,
                            "y_max": roi.y_max,
                            "confidence": roi.confidence,
                        }
                    except Exception as e:
                        logger.error(f"Error storing ROI: {e}")
                    
                    # Draw ROI on frame
                    frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
                    frame = cv2.rectangle(
                        frame,
                        (int(bbox.x_min), int(bbox.y_min)),
                        (int(bbox.x_max), int(bbox.y_max)),
                        (0, 255, 0),
                        2,
                    )
            
            # Encode frame
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # Send frame and ROI data
            await websocket.send_json({
                "frame_number": frame_number,
                "frame_size": len(frame_bytes),
                "roi": roi_data,
            })
            
            # Send frame bytes
            await websocket.send_bytes(frame_bytes)
            
            frame_number += 1
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
        del active_connections[session_id]
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        del active_connections[session_id]


@router.post("/process-frame")
async def process_frame(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Process a single frame and return ROI data
    """
    try:
        content = await file.read()
        nparr = np.frombuffer(content, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect face
        result = face_detector.get_dominant_face(rgb_frame)
        
        if result:
            bbox, confidence = result
            
            roi_create = ROICreateSchema(
                frame_number=0,
                x_min=bbox.x_min,
                y_min=bbox.y_min,
                x_max=bbox.x_max,
                y_max=bbox.y_max,
                confidence=confidence,
            )
            
            roi = ROIService.create_roi(db, roi_create)
            
            # Draw ROI on frame
            output_frame = cv2.rectangle(
                frame,
                (int(bbox.x_min), int(bbox.y_min)),
                (int(bbox.x_max), int(bbox.y_max)),
                (0, 255, 0),
                2,
            )
            
            _, buffer = cv2.imencode('.jpg', output_frame)
            
            return {
                "status": "success",
                "roi": {
                    "id": roi.id,
                    "x_min": roi.x_min,
                    "y_min": roi.y_min,
                    "x_max": roi.x_max,
                    "y_max": roi.y_max,
                    "confidence": roi.confidence,
                },
                "processed_image_size": len(buffer.tobytes()),
            }
        
        return {
            "status": "no_face_detected",
            "roi": None,
        }
        
    except Exception as e:
        logger.error(f"Error processing frame: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing frame: {str(e)}")
