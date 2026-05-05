# System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                         CLIENT BROWSER                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   REACT FRONTEND (Port 3000)                │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │  Video Display & Control                            │   │  │
│  │  │  • HTML5 Canvas for video rendering                 │   │  │
│  │  │  • File upload input                                │   │  │
│  │  │  • WebSocket connection manager                     │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │  ROI Visualization Layer                            │   │  │
│  │  │  • Green bounding box overlay                       │   │  │
│  │  │  • Real-time coordinate display                     │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │  Statistics Dashboard                              │   │  │
│  │  │  • Frame counter                                   │   │  │
│  │  │  • Detection counter                               │   │  │
│  │  │  • Connection status indicator                     │   │  │
│  │  │  • Confidence scores                               │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
      │                                      │                │
      │ File Upload (HTTP POST)              │ WebSocket      │ 
      │                                      │ Connection     │
      │                                      │                │ REST Queries
      ▼                                      ▼                ▼
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│           BACKEND API SERVER (FastAPI - Port 8000)                │
│                        Uvicorn ASGI Server                         │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                   API Routes Layer                          │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │ Video Routes (/api/video/*)                         │   │ │
│  │  │  • POST /upload        → Video file upload          │   │ │
│  │  │  • GET /stream/{id}    → Video streaming (deprecated)    │ │
│  │  │  • WS /ws/{id}         → WebSocket streaming       │   │ │
│  │  │  • POST /process-frame → Single frame processing   │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │ ROI Routes (/api/roi/*)                             │   │ │
│  │  │  • GET /{id}           → Get ROI by ID              │   │ │
│  │  │  • GET /frame/{frame}  → Get ROI by frame number    │   │ │
│  │  │  • GET /session/{sid}  → Get session ROIs           │   │ │
│  │  │  • GET /latest/{sid}   → Get latest detection      │   │ │
│  │  │  • DELETE /{id}        → Delete ROI record          │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │ Health Routes (/api/health/*)                       │   │ │
│  │  │  • GET /                → Service status            │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│  ┌──────────────────────────▼───────────────────────────────────┐ │
│  │                 Service Layer                              │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │ FaceDetectorService                                 │   │ │
│  │  │  ├─ MediaPipe FaceDetection model                   │   │ │
│  │  │  ├─ detect_faces(frame) → BoundingBox[]            │   │ │
│  │  │  ├─ get_dominant_face(frame) → BoundingBox         │   │ │
│  │  │  ├─ draw_roi_on_frame(frame, box) → frame          │   │ │
│  │  │  └─ BoundingBox class (axis-aligned minimal bbox)  │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │ ROIService                                          │   │ │
│  │  │  ├─ create_roi(db, data)                            │   │ │
│  │  │  ├─ get_roi_by_id(db, id)                           │   │ │
│  │  │  ├─ get_roi_by_frame(db, frame_num)                 │   │ │
│  │  │  ├─ get_all_rois(db, filter)                        │   │ │
│  │  │  ├─ get_latest_roi(db, session_id)                  │   │ │
│  │  │  └─ delete_roi(db, id)                              │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│  ┌──────────────────────────▼───────────────────────────────────┐ │
│  │              Data Access Layer (SQLAlchemy ORM)             │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │ Models                                              │   │ │
│  │  │  ├─ ROI                                             │   │ │
│  │  │  │  ├─ id (PK)                                      │   │ │
│  │  │  │  ├─ frame_number                                 │   │ │
│  │  │  │  ├─ x_min, y_min, x_max, y_max (coords)         │   │ │
│  │  │  │  ├─ confidence                                   │   │ │
│  │  │  │  ├─ video_session_id (FK, indexed)              │   │ │
│  │  │  │  └─ created_at                                   │   │ │
│  │  │  ├─ VideoFrame                                      │   │ │
│  │  │  │  ├─ id (PK)                                      │   │ │
│  │  │  │  ├─ frame_number (indexed)                       │   │ │
│  │  │  │  ├─ video_session_id (indexed)                   │   │ │
│  │  │  │  ├─ frame_timestamp                              │   │ │
│  │  │  │  └─ created_at                                   │   │ │
│  │  │  └─ Additional tables (extensible)                  │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │ Schemas (Pydantic)                                  │   │ │
│  │  │  ├─ ROISchema           (full with ID)              │   │ │
│  │  │  ├─ ROICreateSchema     (creation input)            │   │ │
│  │  │  └─ ROIListResponse     (paginated results)         │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│                Connection pooling & Query optimization             │
│                                                                    │
└────────────────────────────────┬─────────────────────────────────┘
                                 │ TCP/IP (Port 5432)
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│              POSTGRESQL DATABASE (Port 5432)                       │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Database: face_detection_db                               │ │
│  │                                                            │ │
│  │  Table: rois                                              │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ id (PK) | frame_no | x_min | y_min | x_max | y_max │  │ │
│  │  │ confidence | video_session_id (FK⬆) | created_at   │  │ │
│  │  │                                                     │  │ │
│  │  │ Indexes:                                            │  │ │
│  │  │  • PK on id (auto)                                  │  │ │
│  │  │  • IDX on frame_number                              │  │ │
│  │  │  • IDX on video_session_id                          │  │ │
│  │  │  • IDX on created_at                                │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │                                                            │ │
│  │  Table: video_frames                                      │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ id (PK) | frame_number (IDX) | video_session_id    │  │ │
│  │  │ frame_timestamp | created_at                        │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │                                                            │ │
│  │  Storage:                                                 │ │
│  │  • Persistent volume for ACID compliance                  │ │
│  │  • Connection pooling: 10 min, 20 max                     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  Query Performance:                                             │
│  • Fast frame lookups (indexed)                               │
│  • Efficient session filtering (indexed)                      │
│  • Pagination support (OFFSET, LIMIT)                        │
│                                                                │
└────────────────────────────────────────────────────────────────┘


DEPLOYMENT CONTAINERS (Docker)
─────────────────────────────────

┌─────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Backend Container  │  │ Frontend Container  │  │ Database Container
│  ──────────────────
│  • Image: python311 │  │  • Image: node18  │  │  • Image: postgres15
│  • Port 8000:8000   │  │  • Port 3000:3000 │  │  • Port 5432:5432
│  • Uvicorn Server   │  │  • Serve static   │  │  • PostgreSQL DB
│  • Auto-reload      │  │  • React App      │  │  • Persistent vol
│  • Vol: /app        │  │  • Vol: /app/src  │  │  • Health check
│                     │  │                   │  │
└─────────────────────┘  └───────────────────┘  └──────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         └───────────────────────┴───────────────────────┘
                      Docker Network
            (face_detection_network - internal)


WORKFLOW: VIDEO FRAME PROCESSING
─────────────────────────────────

Browser sends frame    Decompress/
over WebSocket ──────► decode frame ──────► Convert
                          (JPEG)          BGR→RGB
                                              │
                                              ▼
                                     MediaPipe Face
                                     Detection API
                                       (inference)
                                         │
                        ┌────────────────┼────────────────┐
                        │                │                │
                    No face          One face          Multiple
                    detected         detected          faces
                        │                │                │
                        │          ┌─────▼─────┐         │
                        │          │ Select     │         │
                        │          │ largest    │         │
                        │          │ confidence │         │
                        │          └─────┬─────┘         │
                        │                │                │
                        └────────────────┼────────────────┘
                                         │
                                    BoundingBox
                                   (x_min, y_min,
                                    x_max, y_max)
                                         │
                        ┌────────────────┴────────────────┐
                        │                                 │
                  Create ROISchema              Draw rectangle
                        │                       on frame
                        │                             │
                  Save to DB                    JPEG encode
                        │                             │
                  Return ROI ID ◄──────────────────────┘
                        │
                  Send WebSocket
                  response with ROI
                  + frame bytes
                        │
                        ▼
                  Browser receives
                  Updates canvas display
                  Shows ROI box
```

## Key Components

### Face Detection Pipeline
1. **Input**: Video frame (BGR format from OpenCV or RGB from browser)
2. **Preprocessing**: Convert BGR→RGB if needed
3. **Model**: MediaPipe Face Detection (optimized neural network)
4. **Output**: Bounding boxes with confidence scores
5. **Storage**: Persist to PostgreSQL for analysis

### ROI Calculation
- **Axis-Aligned Minimal Bounding Box (AAMBB)**
- Normalized coordinates → Pixel coordinates
- Stored as (x_min, y_min, x_max, y_max)

### Communication Protocols
- **HTTP**: File upload, configuration endpoints
- **WebSocket**: Low-latency real-time streaming
- **TCP**: Backend ↔ Database communication

### Data Flow
```
User Input → Browser → WebSocket → Backend → Face Detection Service
                                      ↓
                              ROI Service → PostgreSQL
                                      ↓
                           Response → Browser → Visualization
```
