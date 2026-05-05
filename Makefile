.PHONY: help build up down logs test backend-test frontend-test clean install-deps init-db

help:
	@echo "Face Detection Video Streaming System - Available Commands"
	@echo ""
	@echo "Infrastructure:"
	@echo "  make build              Build Docker containers"
	@echo "  make up                 Start all services (docker-compose up)"
	@echo "  make down               Stop all services (docker-compose down)"
	@echo "  make logs               View logs from all containers"
	@echo "  make clean              Remove containers and volumes"
	@echo ""
	@echo "Development:"
	@echo "  make install-deps       Install Python and Node dependencies"
	@echo "  make init-db            Initialize database"
	@echo "  make test               Run all tests"
	@echo "  make backend-test       Run backend tests"
	@echo "  make frontend-test      Run frontend tests"
	@echo ""
	@echo "Utilities:"
	@echo "  make shell-backend      Open bash in backend container"
	@echo "  make shell-db           Connect to PostgreSQL database"
	@echo "  make lint               Lint backend code"
	@echo "  make format             Format backend code"
	@echo ""

build:
	docker-compose build

up:
	docker-compose up -d
	@echo ""
	@echo "✅ Services are running:"
	@echo "   Frontend:   http://localhost:3000"
	@echo "   Backend:    http://localhost:8000"
	@echo "   API Docs:   http://localhost:8000/docs"
	@echo "   Database:   localhost:5432"
	@echo ""

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f postgres

clean:
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf backend/.pytest_cache
	rm -rf frontend/build
	rm -rf frontend/node_modules

install-deps:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "✅ Backend dependencies installed"
	@echo ""
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Frontend dependencies installed"

init-db:
	@echo "Initializing database..."
	docker-compose exec backend python -c "from app.database import init_db; init_db(); print('✅ Database initialized')"

test:
	@echo "Running all tests..."
	cd backend && pytest tests/ -v --tb=short
	@echo "✅ All tests passed"

backend-test:
	@echo "Running backend tests..."
	cd backend && pytest tests/ -v --tb=short

backend-test-coverage:
	@echo "Running backend tests with coverage..."
	cd backend && pytest tests/ --cov=app --cov-report=html
	@echo "✅ Coverage report generated in backend/htmlcov/index.html"

frontend-test:
	@echo "Running frontend tests..."
	cd frontend && npm test

shell-backend:
	docker-compose exec backend bash

shell-db:
	docker-compose exec postgres psql -U user -d face_detection_db

lint:
	@echo "Linting backend code..."
	cd backend && pylint app/ --disable=R,C || true

format:
	@echo "Formatting backend code..."
	cd backend && black app/ tests/ main.py

requirements:
	@echo "Generating requirements.txt..."
	cd backend && pip freeze > requirements.txt.new
	@echo "Review backend/requirements.txt.new and update requirements.txt"

restart:
	docker-compose restart

restart-backend:
	docker-compose restart backend

restart-frontend:
	docker-compose restart frontend

ps:
	docker-compose ps

health:
	@echo "Checking API health..."
	@curl -s http://localhost:8000/api/health/ | jq '.' || echo "Backend not running"

docs:
	@echo "Backend API Documentation:"
	@echo "  Swagger UI: http://localhost:8000/docs"
	@echo "  ReDoc:      http://localhost:8000/redoc"

.DEFAULT_GOAL := help
