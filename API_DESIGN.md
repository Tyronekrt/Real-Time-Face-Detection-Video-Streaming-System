# API Design & Documentation

## Overview

The API follows RESTful principles with WebSocket support for real-time streaming. All responses use JSON format.

## HTTP Semantics

### Status Codes
- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid input or malformed request
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error (logged for debugging)
- **101 Switching Protocols**: WebSocket upgrade successful

### Request Methods
- **GET**: Retrieve resources
- **POST**: Create resources or process data
- **DELETE**: Remove resources
- **WebSocket**: Bidirectional streaming

## Video Endpoints

### Upload Video
```
POST /api/video/upload
Content-Type: multipart/form-data

Body: file (video file)

Response 200:
{
  "status": "success",
  "message": "Video uploaded and queued for processing",
  "video_session_id": "abc123",
  "video_url": "/api/video/stream/abc123",
  "roi_url": "/api/roi/abc123"
}
```

### Stream Video
```
GET /api/video/stream/{session_id}

Response: multipart/x-mixed-replace video stream
```

### WebSocket Streaming
```
WS /api/video/ws/{session_id}

Send: binary frame data (JPEG bytes)

Receive: JSON metadata + frame bytes
{
  "frame_number": 42,
  "frame_size": 5000,
  "roi": {
    "id": 1,
    "frame_number": 42,
    "x_min": 100,
    "y_min": 150,
    "x_max": 400,
    "y_max": 500,
    "confidence": 0.95
  }
}
```

### Process Single Frame
```
POST /api/video/process-frame
Content-Type: multipart/form-data

Body: file (image file)

Response 200:
{
  "status": "success",
  "roi": {
    "id": 1,
    "x_min": 100,
    "y_min": 150,
    "x_max": 400,
    "y_max": 500,
    "confidence": 0.95
  },
  "processed_image_size": 5000
}

Response when no face detected:
{
  "status": "no_face_detected",
  "roi": null
}
```

## ROI Endpoints

### Get ROI by ID
```
GET /api/roi/{roi_id}

Response 200:
{
  "id": 1,
  "frame_number": 42,
  "x_min": 100.0,
  "y_min": 150.0,
  "x_max": 400.0,
  "y_max": 500.0,
  "confidence": 0.95,
  "video_session_id": "abc123",
  "created_at": "2024-01-15T10:30:00"
}
```

### Get ROI by Frame
```
GET /api/roi/frame/{frame_number}

Response 200: Single ROI object (same as above)
```

### Get Session ROIs
```
GET /api/roi/session/{session_id}?skip=0&limit=100

Response 200:
{
  "total": 50,
  "rois": [
    { roi_object_1 },
    { roi_object_2 },
    ...
  ]
}
```

### Get All ROIs
```
GET /api/roi/?skip=0&limit=100&video_session_id=optional_id

Response 200: Same as session ROIs endpoint
```

### Get Latest ROI
```
GET /api/roi/latest/{session_id}

Response 200: Latest ROI object
```

### Delete ROI
```
DELETE /api/roi/{roi_id}

Response 200:
{
  "status": "success",
  "message": "ROI 1 deleted successfully"
}
```

## Error Responses

### Bad Request (400)
```json
{
  "detail": "Invalid frame data"
}
```

### Not Found (404)
```json
{
  "detail": "ROI not found"
}
```

### Server Error (500)
```json
{
  "detail": "Error processing video: [error message]"
}
```

## Query Parameters

### Pagination
- `skip` (int, default=0): Number of records to skip
- `limit` (int, default=100, max=1000): Maximum records to return

### Filtering
- `video_session_id` (string, optional): Filter by video session

## Request/Response Format

All JSON requests should include:
```
Content-Type: application/json
```

All JSON responses include:
```
Content-Type: application/json
```

## Rate Limiting

Not enforced in current version, but production deployment should include:
- Per-IP rate limiting
- Per-session limits for WebSocket connections

## CORS Headers

The API includes CORS headers for allowed origins:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

## Versioning

Current version: 1.0.0

Future versions will be available at:
- `/api/v2/...` (backward compatibility maintained)
