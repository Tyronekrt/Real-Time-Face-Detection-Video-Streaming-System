# Testing Guide

## Test Strategy

### Test Pyramid

```
        ▲
       / \
      /   \  End-to-End (Integration)
     /     \  [5-10% of tests]
    /-------\
   /         \
  /           \ Integration Tests
 /             \ [20-30% of tests]
/-------────────\
                 Unit Tests
             [60-80% of tests]
```

## Unit Tests

Test individual functions and classes in isolation.

### Running Unit Tests

```bash
cd backend
pytest tests/ -v

# Specific test file
pytest tests/test_face_detector.py -v

# Specific test function
pytest tests/test_roi.py::test_create_roi -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Unit Test Categories

#### 1. Face Detection Service (`test_face_detector.py`)

```python
# Test BoundingBox creation
def test_bounding_box_creation():
    bbox = BoundingBox(10, 20, 100, 200)
    assert bbox.width == 90
    assert bbox.height == 180

# Test face detector initialization
def test_face_detector_initialization():
    detector = FaceDetectorService(confidence_threshold=0.5)
    assert detector.confidence_threshold == 0.5

# Test frame without faces
def test_detect_faces_on_random_frame():
    detector = FaceDetectorService()
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    boxes, confidences = detector.detect_faces(frame)
    assert isinstance(boxes, list)
```

#### 2. ROI Service (`test_roi.py`)

```python
# Test ROI creation
def test_create_roi(test_session):
    roi_data = ROICreateSchema(...)
    roi = ROIService.create_roi(test_session, roi_data)
    assert roi.id is not None

# Test ROI retrieval
def test_get_roi_by_id(test_session):
    roi = ROIService.get_roi_by_id(test_session, roi_id)
    assert retrieved.id == roi_id

# Test ROI deletion
def test_delete_roi(test_session):
    success = ROIService.delete_roi(test_session, roi_id)
    assert success is True
```

#### 3. Health Endpoints (`test_health.py`)

```python
# Test health check
def test_health_check(client):
    response = client.get("/api/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

## Integration Tests

Test multiple components working together.

### API Integration Tests

```python
# Test file upload endpoint
def test_upload_video_integration(client):
    with open('sample_video.mp4', 'rb') as f:
        response = client.post('/api/video/upload', 
                              files={'file': f})
    assert response.status_code == 200
    assert 'video_session_id' in response.json()

# Test ROI retrieval after detection
def test_detect_and_retrieve_flow(client, test_session):
    # 1. Process frame
    response = client.post('/api/video/process-frame',
                          files={'file': image_file})
    roi_id = response.json()['roi']['id']
    
    # 2. Retrieve ROI
    roi_response = client.get(f'/api/roi/{roi_id}')
    assert roi_response.status_code == 200
    assert roi_response.json()['id'] == roi_id
```

### Database Integration Tests

```python
# Test transaction rollback
def test_roi_creation_with_rollback(test_session):
    try:
        # Create invalid ROI
        invalid_roi = ROICreateSchema(frame_number=-1, ...)
        ROIService.create_roi(test_session, invalid_roi)
    except Exception:
        test_session.rollback()
    
    # Verify not in database
    rois = test_session.query(ROI).all()
    assert len(rois) == 0
```

### WebSocket Integration Tests

```python
# Test WebSocket connection and frame streaming
@pytest.mark.asyncio
async def test_websocket_streaming(client):
    with client.websocket_connect('/api/video/ws/test-session') as ws:
        # Send frame data
        frame_bytes = b'fake_frame_data'
        ws.send_bytes(frame_bytes)
        
        # Receive response
        data = ws.receive_json()
        assert 'frame_number' in data
        
        # Receive frame data
        frame_response = ws.receive_bytes()
        assert len(frame_response) > 0
```

## End-to-End Tests

Test complete workflows through the UI.

### Manual E2E Testing

1. **Upload Flow**
   - [ ] Open frontend
   - [ ] Click "Upload Video"
   - [ ] Select video file
   - [ ] Wait for processing
   - [ ] Verify ROI displayed
   - [ ] Check statistics updated

2. **Webcam Stream**
   - [ ] Click "Start Webcam"
   - [ ] Allow browser permissions
   - [ ] Face detection active
   - [ ] ROI overlay visible
   - [ ] Statistics updating
   - [ ] Can see connection status

3. **API Endpoints**
   - [ ] GET /api/health/ returns 200
   - [ ] POST /api/video/upload works
   - [ ] GET /api/roi/ pagination works
   - [ ] DELETE /api/roi/{id} successful
   - [ ] WebSocket connection stable

### Automated E2E Tests (Selenium/Cypress)

```javascript
// test_e2e.js
describe('Face Detection App', () => {
  it('should display webcam stream', () => {
    cy.visit('http://localhost:3000');
    cy.contains('Start Webcam').click();
    cy.get('.video-canvas').should('be.visible');
  });

  it('should uploadvideo file', () => {
    cy.visit('http://localhost:3000');
    cy.get('input[type=file]').selectFile('sample.mp4');
    cy.contains('success').should('be.visible');
  });

  it('should display ROI on detection', () => {
    // Start stream
    // Wait for detection
    cy.get('.roi-box').should('be.visible');
  });
});
```

Run with:
```bash
cd frontend
npx cypress run
```

## Performance Testing

### Load Testing

Use Apache JMeter or similar:

```bash
# Test API with 100 concurrent users for 5 minutes
jmeter -n -t test_plan.jmx \
  -Jusers=100 \
  -Jrampup=60 \
  -Jduration=300 \
  -l results.jtl
```

### Stress Testing

Gradually increase load to find breaking point:

```python
# stress_test.py
import concurrent.futures
import time
import requests

def hit_api():
    response = requests.get('http://localhost:8000/api/roi')
    return response.status_code == 200

# Start with 10 concurrent tasks, increase gradually
for concurrency in [10, 50, 100, 500, 1000]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(hit_api) for _ in range(concurrency)]
        results = [f.result() for f in futures]
        success_rate = sum(results) / len(results)
        print(f"Concurrency {concurrency}: {success_rate*100}% success")
        time.sleep(1)
```

### Load Test Results

Expected results:
- 1000 req/sec API throughput
- <100ms p95 latency
- <50MB memory per backend instance
- <80% CPU utilization

## Security Testing

### CORS Testing

```bash
# Verify CORS headers
curl -H "Origin: http://malicious.com" \
  -H "Access-Control-Request-Method: GET" \
  http://localhost:8000/api/roi
# Should NOT include malicious.com in Access-Control-Allow-Origin
```

### SQL Injection Testing

```python
# Test parameterized queries
def test_sql_injection_protection():
    malicious_input = "'; DROP TABLE rois; --"
    
    # Should not execute; should escape properly
    rois = ROIService.get_all_rois(
        db, 
        video_session_id=malicious_input
    )
    # Verify rois table still exists
    assert db.query(ROI).count() >= 0
```

### Authentication Testing

```bash
# Test without credentials
curl http://localhost:8000/api/roi

# Test with invalid token
curl -H "Authorization: Bearer invalid_token" \
  http://localhost:8000/api/roi

# Test with expired token
# ... similar
```

## Coverage Reports

```bash
# Generate coverage report
cd backend
pytest tests/ --cov=app --cov-report=html

# View report
open htmlcov/index.html
```

Target coverage:
- **Overall**: >80%
- **Services**: >90%
- **Routes**: >80%
- **Models**: >70%

## Test Fixtures & Mocking

### Database Fixtures

```python
# conftest.py
@pytest.fixture
def test_db():
    """In-memory SQLite database for testing"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def test_session(test_db):
    """Create test database session"""
    connection = test_db.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()
```

### Mock Services

```python
# mock_face_detector.py
from unittest.mock import Mock
from app.services.face_detector import BoundingBox

def mock_face_detector():
    detector = Mock()
    detector.get_dominant_face.return_value = (
        BoundingBox(100, 100, 200, 200),
        0.95
    )
    return detector

# Use in tests
def test_with_mock():
    detector = mock_face_detector()
    result = detector.get_dominant_face(dummy_frame)
    assert result[1] == 0.95  # confidence
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: password
          POSTGRES_DB: test_db

    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      
      - name: Run tests
        run: |
          cd backend && pytest tests/ -v --cov=app
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Test Checklist

Before deployment:
- [ ] All unit tests passing
- [ ] Coverage >80%
- [ ] Integration tests passing
- [ ] Load tests acceptable
- [ ] Security tests passed
- [ ] No critical issues in SAST
- [ ] Documentation tests passing
- [ ] E2E tests successful

---

For testing best practices, see:
- pytest docs: https://docs.pytest.org/
- Cypress docs: https://docs.cypress.io/
- Load testing tools: https://jmeter.apache.org/
