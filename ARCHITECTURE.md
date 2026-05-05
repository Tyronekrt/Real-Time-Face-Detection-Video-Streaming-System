# Architecture & Design

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT BROWSER                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │          React Frontend (Port 3000)              │   │
│  │  • Video Canvas                                  │   │
│  │  • ROI Visualization                             │   │
│  │  • Statistics Dashboard                          │   │
│  │  • WebSocket Client                              │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         │                      │
         │ HTTP/REST           │ WebSocket
         │                      │
         ▼                      ▼
┌─────────────────────────────────────────────────────────┐
│              BACKEND API LAYER (Port 8000)              │
│                  FastAPI + Uvicorn                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              API Routes                         │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  • /api/video/upload    (Video Upload)         │   │
│  │  • /api/video/stream    (Video Stream)         │   │
│  │  • /api/video/ws        (WebSocket)            │   │
│  │  • /api/video/process   (Frame Processing)     │   │
│  │  • /api/roi/*           (ROI Operations)       │   │
│  │  • /api/health          (Health Check)         │   │
│  └─────────────────────────────────────────────────┘   │
│                         │                               │
│  ┌──────────────────────▼──────────────────────────┐   │
│  │          SERVICE LAYER                         │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  FaceDetectorService                           │   │
│  │  • MediaPipe face detection                    │   │
│  │  • BoundingBox calculation                     │   │
│  │  • Frame processing                            │   │
│  │                                                │   │
│  │  ROIService                                    │   │
│  │  • Database CRUD operations                    │   │
│  │  • Query optimization                          │   │
│  └─────────────────────────────────────────────────┘   │
│                         │                               │
│  ┌──────────────────────▼──────────────────────────┐   │
│  │     DATA ACCESS LAYER (SQLAlchemy ORM)         │   │
│  │  • Database models                             │   │
│  │  • Relationships                               │   │
│  │  • Schema validation (Pydantic)                │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         │
         │ TCP Connection (Port 5432)
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│           DATABASE LAYER (PostgreSQL)                   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Tables:                                         │   │
│  │  • rois (ROI data with indices)                │   │
│  │  • video_frames (Frame metadata)               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Component Breakdown

### Frontend (React)
**Purpose**: User interface for video display and ROI visualization

**Components**:
- `App.js`: Main component managing state and connections
- `App.css`: Responsive styling

**Features**:
- Webcam/video file upload
- WebSocket connection management
- Real-time frame rendering
- ROI overlay visualization
- Statistics dashboard

### Backend API (FastAPI)
**Purpose**: Core business logic and video processing

**Layers**:

1. **Routes Layer** (`app/routes/`)
   - `video.py`: Video endpoints (upload, stream, WebSocket)
   - `roi.py`: ROI data endpoints (CRUD operations)
   - `health.py`: Health check

2. **Services Layer** (`app/services/`)
   - `face_detector.py`: Face detection using MediaPipe
   - `roi_service.py`: Database operations for ROIs

3. **Models Layer** (`app/models/`)
   - `roi.py`: SQLAlchemy ORM models
   - Database tables definition

4. **Schemas Layer** (`app/schemas/`)
   - `roi.py`: Pydantic validation schemas
   - Request/response validation

### Database (PostgreSQL)
**Purpose**: Persistent storage of ROI data

**Tables**:
- `rois`: Detected face regions
- `video_frames`: Frame metadata

**Indexes**:
- `frame_number` (for quick lookup)
- `video_session_id` (for filtering by session)

## Data Flow

### 1. Video Upload Flow
```
User Upload → FormData → POST /video/upload → Generate SessionID 
           → Return URLs → Client stores SessionID
```

### 2. WebSocket Streaming Flow
```
Browser Video Input → Capture Frame → JavaScript Canvas → Image Data
                   ↓
               WebSocket Frame → Backend receives bytes
                                ↓
                  Convert to Numpy Array → Face Detection
                                ↓
                  MediaPipe Detection → Get BoundingBox
                                ↓
                  Create ROI Schema → Store in Database
                                ↓
                  Draw Rectangle on Frame → Encode as JPEG
                                ↓
                  Send Frame Metadata + Frame Bytes → WebSocket Response
                                ↓
                  Browser receives data → Update Canvas → Display with ROI
```

### 3. ROI Query Flow
```
GET /roi/session/{session_id} → Query Database
                               ↓
                    Apply Pagination (skip, limit)
                               ↓
                    Serialize to JSON (Pydantic)
                               ↓
                    Return to Client with HTTP 200
```

## Separation of Concerns

### API Routes
- **Responsibility**: Handle HTTP requests/responses
- **Does NOT**: Process frames, perform calculations
- **Delegates to**: Services

### Services
- **Responsibility**: Business logic implementation
- **Does NOT**: Handle HTTP, database queries directly
- **Delegates to**: Models, external libraries

### Models
- **Responsibility**: Database schema and persistence
- **Does NOT**: Handle business logic, HTTP
- **Delegates to**: Database engine (SQLAlchemy)

### Schemas
- **Responsibility**: Data validation and serialization
- **Does NOT**: Database access, processing
- **Used by**: Routes for validation

## Error Handling Strategy

```
┌─────────────────────────────────────────┐
│         Request Arrives                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    Route Handler (Routes Layer)         │
│    • Validate input (Pydantic)          │
│    • Call service                       │
└──────────────┬──────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
    Success        Exception
        │             │
        │      ┌──────▼──────────────────┐
        │      │  Logger (audit trail)   │
        │      └──────┬──────────────────┘
        │             │
        │      ┌──────▼──────────────────┐
        │      │  HTTPException          │
        │      │  with status code       │
        │      └──────┬──────────────────┘
        │             │
        └─────────┬───┘
                  │
                  ▼
        ┌─────────────────────┐
        │  HTTP Response      │
        │  (200, 400, 500)    │
        │  JSON Error Message │
        └─────────────────────┘
```

## Security Architecture

### CORS Protection
- Whitelist allowed origins
- Only http://localhost:3000 in development
- Configure for production domains

### Input Validation
- Pydantic schemas validate all inputs
- Type checking on all parameters
- File size limits on uploads

### SQL Injection Prevention
- SQLAlchemy parameterized queries
- ORM-based database access
- No raw SQL strings

### Error Information Leakage
- Generic error messages to clients
- Detailed logging server-side only
- Stack traces never exposed to frontend

## Performance Optimizations

### Database
- Connection pooling (pool_size=10, max_overflow=20)
- Indexes on frequently queried columns
- Pagination limits results
- Query optimization with proper joins

### API
- GZIP compression middleware
- Async processing with FastAPI
- HTTP cache headers
- Connection keep-alive

### Frontend
- Canvas-based rendering (faster than DOM)
- Debounced updates
- Efficient state management

## Scalability Considerations

### Current Capacity
- Single-threaded video processing
- Single database instance
- Direct backend-to-database connection

### Future Improvements
1. **Message Queue**: Celery for background processing
2. **Caching**: Redis for ROI data cache
3. **Load Balancing**: Nginx reverse proxy
4. **Database Optimization**: Replication, sharding
5. **CDN**: Static asset delivery
6. **Monitoring**: Prometheus + Grafana

## Testing Strategy

### Unit Tests
- `test_face_detector.py`: Face detection logic
- `test_roi.py`: ROI database operations
- `test_health.py`: Health endpoints

### Integration Tests
- Full API workflow tests
- Database transaction tests
- WebSocket communication tests

### Manual Testing
- Real camera device testing
- Video file processing
- Concurrent user simulation

## Deployment Architecture

### Docker Structure
```
Backend Container         Frontend Container       Database Container
└─ Uvicorn Server        └─ Node HTTP Server     └─ PostgreSQL
   • FastAPI App            • React App             • Tables
   • Port 8000              • Port 3000             • Port 5432
```

### Network
- Internal Docker network: `face_detection_network`
- Exposed ports: 3000, 8000, 5432
- Volume mounts for development

### Hot Reload
- Backend: `uvicorn --reload` enabled
- Frontend: React dev server HMR
- Allows rapid development iteration
