# Real-Time Face Detection Video Streaming System

🎥 A production-ready containerized system for real-time face detection and ROI (Region of Interest) tracking with a modern web interface.

## 🌟 Features

- **Real-time Face Detection**: Uses MediaPipe for robust face detection without OpenCV dependencies
- **WebSocket Streaming**: Live video streaming with low-latency updates
- **ROI Tracking**: Stores detected face regions in PostgreSQL database
- **REST API**: Three dedicated endpoints for video upload, streaming, and ROI data retrieval
- **React Frontend**: Modern, responsive UI for real-time visualization
- **Docker Containerization**: Easy deployment with Docker Compose
- **Production Ready**: Includes error handling, logging, and comprehensive testing

## 📋 Quick Start (5 Minutes)

### Prerequisites
- Docker & Docker Compose installed
- Git

### Installation & Running

```bash
# Clone and navigate
cd /path/to/project

# Start all services
docker-compose up --build

# Services will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Database: localhost:5432
```

That's it! 🚀 Open http://localhost:3000 in your browser.

## 📁 Project Structure

```
.
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── routes/             # API endpoints
│   │   ├── schemas/            # Pydantic validation schemas
│   │   ├── services/           # Business logic
│   │   │   ├── face_detector.py    # Face detection service
│   │   │   └── roi_service.py      # ROI database operations
│   │   ├── config.py          # Configuration management
│   │   └── database.py        # Database setup
│   ├── tests/                 # Unit and integration tests
│   ├── main.py               # FastAPI app entry point
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── App.js            # Main component
│   │   ├── App.css           # Responsive styling
│   │   └── index.js          # React root
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml         # Multi-container orchestration
└── README.md
```

## 🔌 API Endpoints

### Video Streaming
- **POST** `/api/video/upload` - Upload video file for processing
- **GET** `/api/video/stream/{session_id}` - Stream processed video
- **WS** `/api/video/ws/{session_id}` - WebSocket for real-time frame streaming
- **POST** `/api/video/process-frame` - Process individual frame

### ROI Data
- **GET** `/api/roi/{roi_id}` - Get specific ROI by ID
- **GET** `/api/roi/frame/{frame_number}` - Get ROI for frame
- **GET** `/api/roi/session/{session_id}` - Get all ROIs for session
- **GET** `/api/roi/latest/{session_id}` - Get latest detected face
- **DELETE** `/api/roi/{roi_id}` - Delete ROI record

### Health
- **GET** `/api/health/` - Service health check

## 🗄️ Database Schema

### `rois` Table
Stores detected face regions of interest:
```sql
- id (Integer, Primary Key)
- frame_number (Integer)
- x_min, y_min, x_max, y_max (Float) - Bounding box coordinates
- confidence (Float) - Detection confidence score (0-1)
- video_session_id (String) - Links to video session
- created_at (DateTime)
```

### `video_frames` Table
Tracks frame metadata:
```sql
- id (Integer, Primary Key)
- frame_number (Integer, Indexed)
- video_session_id (String, Indexed)
- frame_timestamp (DateTime)
- created_at (DateTime)
```

## 🛠️ Technology Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - ORM for database operations
- PostgreSQL - Relational database
- MediaPipe - ML library for face detection
- Uvicorn - ASGI server
- WebSockets - Real-time bidirectional communication

**Frontend:**
- React 18 - UI library
- Axios - HTTP client
- CSS3 - Responsive styling
- WebSocket API

**DevOps:**
- Docker & Docker Compose
- Multi-stage builds for optimized images

## 🎯 Architecture & Design Decisions

### Why MediaPipe instead of OpenCV?
- Lightweight and optimized for face detection
- Better performance for single-face scenarios
- Lower memory footprint
- Out-of-box pre-trained models

### Bounding Box Drawing (Without OpenCV)
Implemented custom pixel manipulation to draw ROI rectangles:
- Direct numpy array pixel modification
- Works with any image format
- No external dependencies for drawing

### WebSocket vs REST for Streaming
- **WebSocket**: Low-latency, continuous connection for real-time updates
- **REST**: Stateless, easier to scale, used for single frame processing

### Database Choice: PostgreSQL
- Strong ACID compliance for ROI data integrity
- Efficient indexing for fast queries by session/frame
- Supports complex queries for analytics
- Industry standard for production systems

## 🧪 Testing

Run tests:
```bash
cd backend
pytest tests/ -v
```

Test coverage includes:
- Health check endpoints
- ROI CRUD operations
- Face detection service
- Database models

## 🔒 Security Features

1. **CORS Protection**: Configured allowed origins
2. **Input Validation**: Pydantic schemas validate all inputs
3. **SQL Injection Prevention**: SQLAlchemy parameterized queries
4. **Error Handling**: Comprehensive error messages without exposing internals
5. **Logging**: Detailed audit trail for debugging

## 📊 Performance Considerations

1. **Frame Buffering**: Configurable buffer for smooth streaming
2. **Lazy Loading**: Database queries optimized with pagination
3. **GZIP Compression**: Reduces response payload size
4. **Connection Pooling**: Efficient database connection management
5. **Async Processing**: Non-blocking I/O for concurrent requests

## 📈 Scalability Enhancements (Future)

1. Redis caching for frequently accessed ROIs
2. Message queue (Celery) for background processing
3. Load balancing with Nginx
4. Database replication and sharding
5. CDN for static assets

## 🐛 Error Handling

- **400 Bad Request**: Invalid input parameters
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Server-side errors with logging
- **WebSocket Errors**: Graceful disconnect handling

## 📝 Git Commit History

The project follows proper commit conventions:
```
- feat: Add face detection service
- feat: Implement WebSocket streaming endpoint
- feat: Create React frontend with ROI visualization
- chore: Add Docker configuration
- test: Add unit tests for ROI service
```

## 🔄 Development Workflow

1. Create feature branch: `git checkout -b feature/name`
2. Make changes and commit: `git commit -m "feat: description"`
3. Push to remote: `git push origin feature/name`
4. Create pull request for review

## 📚 API Documentation

Automatic interactive docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🎨 Frontend Features

- **Real-time Video Display**: Canvas-based rendering
- **ROI Visualization**: Green bounding box overlay
- **Statistics Dashboard**: Frame count, face detection count
- **Responsive Design**: Works on desktop and tablet
- **Status Indicator**: Visual connection status

## 🚀 Deployment

### Production Checklist
- [ ] Set strong database password
- [ ] Configure environment variables
- [ ] Enable HTTPS
- [ ] Set up monitoring and alerts
- [ ] Configure backup strategy
- [ ] Review security policies
- [ ] Load test the system
- [ ] Set up CI/CD pipeline

## 💡 Example Usage

```python
# Python client example
import requests

# Detect face in image
with open('image.jpg', 'rb') as f:
    response = requests.post('http://localhost:8000/api/video/process-frame', 
                            files={'file': f})
    roi_data = response.json()['roi']
    print(f"Face detected at: ({roi_data['x_min']}, {roi_data['y_min']})")

# Get ROI data
response = requests.get('http://localhost:8000/api/roi')
all_rois = response.json()['rois']
```

## 📞 Support & Contributing

For issues, feature requests, or contributions, please open an issue or PR.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- MediaPipe team for excellent ML models
- FastAPI community for the framework
- React team for UI library
- All contributors and testers

---

**Built with ❤️ for real-time face detection**
