# Setup & Development Guide

## 📋 Prerequisites

- Docker & Docker Compose (for containerized deployment)
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- PostgreSQL 15+ (for local database)
- Git

## 🚀 Quick Start (5 Minutes)

### Option 1: With Docker (Recommended)

```bash
# Clone repository
cd /path/to/project

# Start all services
docker-compose up --build

# Services will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

That's it! Open http://localhost:3000 in your browser. ✨

### Option 2: Local Development Setup

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run database
docker run -d \
  --name postgres_dev \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=face_detection_db \
  -p 5432:5432 \
  postgres:15-alpine

# Initialize database
python -c "from app.database import init_db; init_db()"

# Start backend server
uvicorn main:app --reload --port 8000
```

#### Frontend Setup

```bash
# In another terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server (requires backend running)
REACT_APP_API_URL=http://localhost:8000 npm start
```

The frontend will open at http://localhost:3000

## 🧪 Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Specific test file
pytest tests/test_roi.py -v

# Frontend tests
cd frontend
npm test
```

## 📊 Database Setup

### Initial Setup
```bash
# Initialize tables
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

### Connect to Database
```bash
# Using docker-compose
docker-compose exec postgres psql -U user -d face_detection_db

# Or directly
psql postgresql://user:password@localhost:5432/face_detection_db
```

### Sample Queries
```sql
-- View all ROIs
SELECT * FROM rois ORDER BY created_at DESC;

-- ROIs for specific session
SELECT * FROM rois WHERE video_session_id = 'session-id';

-- Count detections per frame
SELECT frame_number, COUNT(*) as count FROM rois GROUP BY frame_number;

-- Recent detections
SELECT * FROM rois ORDER BY created_at DESC LIMIT 10;
```

## 🛠️ Development Workflow

### Making Changes

1. **Backend Changes**
   - Modify files in `backend/app/`
   - Changes auto-reload with `--reload` flag
   - Test with `pytest`

2. **Frontend Changes**
   - Modify files in `frontend/src/`
   - Hot reload automatically triggers
   - Test with `npm test`

3. **Database Changes**
   - Modify models in `backend/app/models/`
   - Run migrations or recreate database
   - Test with `pytest`

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/your-feature

# Create pull request for review
```

### Commit Message Format

Follow conventional commits:
- `feat: Add new feature`
- `fix: Fix bug in component`
- `docs: Update documentation`
- `test: Add tests for feature`
- `chore: Update dependencies`
- `refactor: Restructure code`

## 📝 Common Tasks

### Using Makefile (Recommended)

```bash
# View all available commands
make help

# Build containers
make build

# Start services
make up

# View logs
make logs

# Run tests
make test

# Connect to database
make shell-db

# Run shell in backend container
make shell-backend

# Check API health
make health
```

### Manual Docker Commands

```bash
# Build specific container
docker-compose build backend

# View running containers
docker-compose ps

# View logs from specific service
docker-compose logs backend

# Stop and remove containers
docker-compose down

# Remove volumes as well (careful!)
docker-compose down -v

# Execute command in container
docker-compose exec backend bash

# Rebuild after code changes
docker-compose up --build
```

## 🔍 Debugging

### Backend Debugging

```python
# Add logging in code
import logging
logger = logging.getLogger(__name__)
logger.info("Debug message")
logger.error("Error message")

# View logs
docker-compose logs backend

# Connect to Python debugger
import pdb; pdb.set_trace()
```

### Frontend Debugging

```javascript
// Browser DevTools Console
console.log("Debug message");
console.error("Error message");

// React DevTools browser extension
// Redux DevTools (if using Redux)

// Network tab to inspect API calls
```

### Database Debugging

```bash
# Connect to database
docker-compose exec postgres psql -U user -d face_detection_db

# Run queries to check data
\dt  -- List tables
SELECT * FROM rois LIMIT 5;
\d rois  -- Describe table structure
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :3000   # Frontend
lsof -i :8000   # Backend
lsof -i :5432   # Database

# Kill process (on Linux/Mac)
kill -9 <PID>

# Or use different ports in docker-compose.yml
```

### Database Connection Error
```bash
# Check if database is running
docker-compose ps

# Check database logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres

# Reinitialize if corrupted
docker-compose down -v
docker-compose up postgres
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

### Frontend API Connection Error
```bash
# Verify backend is running
curl http://localhost:8000/api/health/

# Check CORS configuration in backend/app/config.py
# Ensure frontend URL is in ALLOWED_ORIGINS

# Check browser console for CORS errors
# Check backend logs for incoming requests
```

### Face Detection Not Working
```bash
# Verify MediaPipe is installed
python -c "import mediapipe; print(mediapipe.__version__)"

# Check model can load
python -c "from app.services.face_detector import FaceDetectorService; print('OK')"

# Test with static image
# See backend tests for examples
```

## 📦 Dependency Management

### Backend Dependencies
```bash
# Add new dependency
pip install new-package
pip freeze > backend/requirements.txt

# Update all dependencies
pip install --upgrade -r backend/requirements.txt
```

### Frontend Dependencies
```bash
# Add new dependency
cd frontend
npm install new-package

# Update package.json and package-lock.json
# Commit both files to git
```

## 🚢 Production Deployment

### Pre-deployment Checklist

- [ ] Set `DEBUG=False` in environment
- [ ] Use strong database password
- [ ] Configure HTTPS/TLS
- [ ] Set up monitoring and alerting
- [ ] Configure backups
- [ ] Review CORS and security settings
- [ ] Load test the system
- [ ] Set up CI/CD pipeline

### Environment Variables

Create `.env` for production:
```
DATABASE_URL=postgresql://prod_user:strong_password@db-host:5432/prod_db
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
SECURE_COOKIES=True
```

### Docker Deployment

```bash
# Build production images
docker-compose -f docker-compose.yml build

# Push to registry
docker tag backend:latest yourregistry/backend:v1.0
docker push yourregistry/backend:v1.0

# Deploy using orchestration (Kubernetes, Docker Swarm, etc.)
```

### Health Checks

```bash
# Monitor API health
curl -s http://your-domain/api/health/ | jq .

# Monitor database
docker-compose exec postgres pg_isready

# Monitor containers
docker-compose ps
docker-compose logs
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [MediaPipe Face Detection](https://google.github.io/mediapipe/solutions/face_detection)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

## 🆘 Getting Help

1. Check the README.md
2. Review ARCHITECTURE.md for design decisions
3. Check API_DESIGN.md for API details
4. Review existing tests for usage examples
5. Check container logs for errors
6. Consult inline code comments
