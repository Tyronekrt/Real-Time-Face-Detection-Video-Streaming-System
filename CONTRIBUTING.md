# Contributing Guidelines

## Welcome!

Thank you for your interest in contributing to the Real-Time Face Detection Video Streaming System!

## Getting Started

1. **Fork the repository**
2. **Clone your fork locally**
   ```bash
   git clone https://github.com/yourusername/face-detection.git
   cd face-detection
   ```

3. **Set up development environment**
   ```bash
   # Using Make (recommended)
   make install-deps
   
   # Or manually:
   cd backend && pip install -r requirements.txt
   cd ../frontend && npm install
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Backend Changes

```bash
# Navigate to backend
cd backend

# Make sure Docker database is running
docker-compose up postgres

# Run tests before committing
pytest tests/ -v

# Check coverage
pytest tests/ --cov=app --cov-report=html

# Start development server
uvicorn main:app --reload --port 8000
```

### Frontend Changes

```bash
# Navigate to frontend
cd frontend

# Install new dependencies if needed
npm install

# Start dev server (backend must be running)
npm start

# Run tests
npm test
```

### Testing Requirements

- **Backend**: Aim for >80% code coverage
- **Frontend**: Test critical user flows
- All tests must pass before PR submission

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): subject

body

footer
```

### Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `chore`: Build, dependencies, tooling
- `refactor`: Code restructuring without feature changes
- `perf`: Performance improvements

### Examples:
```
feat(video): implement streaming endpoint

test(roi): add coverage for ROI queries

fix(face-detector): handle empty frames gracefully

docs: update API documentation
```

## Pull Request Process

1. **Before submitting:**
   - [ ] All tests pass
   - [ ] Code follows project style
   - [ ] Documentation updated
   - [ ] No debug code left behind

2. **Create PR with description:**
   - What does it fix/add?
   - Why is this needed?
   - How was it tested?

3. **Code review process:**
   - At least one approval required
   - Address feedback in follow-up commits
   - Keep PR focused on one feature/bug

## Code Style

### Python

Follow PEP 8 with these guidelines:

```python
# Use type hints
def detect_faces(frame: np.ndarray) -> List[BoundingBox]:
    """Detect faces in frame.
    
    Args:
        frame: Input frame as RGB numpy array
        
    Returns:
        List of detected bounding boxes
    """
    pass

# Use descriptive names
roi_data = {}  # Good
r = {}         # Bad

# Add docstrings to functions and classes
class FaceDetectorService:
    """Service for face detection operations."""
    pass
```

### JavaScript/React

```javascript
// Use arrow functions
const handleClick = () => { };

// Use meaningful component names
const VideoDisplay = () => { };  // Good
const Comp = () => { };          // Bad

// Add JSDoc comments
/**
 * Display video feed with ROI overlay
 * @param {Object} props - Component props
 * @param {HTMLVideoElement} props.video - Video element
 * @returns {JSX.Element} Video display component
 */
const VideoDisplay = ({ video }) => {
  // ...
};
```

## Architecture & Design Decisions

When making architectural changes:

1. **Document the decision** in ARCHITECTURE.md
2. **Explain the trade-offs**
3. **Consider performance impact**
4. **Update related tests**

## Reporting Issues

Use GitHub Issues with clear descriptions:

```markdown
## Description
What's the problem?

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen?

## Actual Behavior
What actually happens?

## Environment
- OS: Linux/Mac/Windows
- Python version: 3.11
- Browser: Chrome 120
```

## Security

Report security vulnerabilities **privately**:
- Do NOT create public GitHub issues
- Email: security@example.com
- Include proof of concept if possible

## Performance Considerations

When submitting changes:

- **Before:** What was the performance?
- **After:** What is it now?
- **Metrics:** Request latency, memory usage, CPU

Example:
```
Before: API responds in 150ms average
After: API responds in 85ms average (43% improvement)
```

## Documentation

All features need documentation:

1. **Code comments** for complex logic
2. **Docstrings** for all functions/classes
3. **README** update for new features
4. **API_DESIGN.md** for API changes
5. **ARCHITECTURE.md** for structural changes

## Useful Commands

```bash
# View all available make targets
make help

# Run backend tests with coverage
make backend-test-coverage

# Connect to database
make shell-db

# View logs from specific service
make logs-backend

# Format code (Python)
make format

# Lint code (Python)
make lint
```

## Questions?

- Check existing documentation
- Search closed issues
- Open a discussion issue
- Ask in pull request comments

## Code of Conduct

- Be respectful and inclusive
- Assume good faith
- Focus on the code, not the person
- Provide constructive feedback

## Thank You!

Your contributions help make this project better for everyone. 🙏

---

Happy coding! 🚀
