# Deployment Guide

## Production Deployment

### System Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 20GB SSD storage
- Linux (Ubuntu 20.04 or later recommended)

**Recommended:**
- 4+ CPU cores
- 8GB+ RAM
- 50GB+ SSD storage
- Load balancer in front
- Backup storage

### Pre-deployment Checklist

- [ ] Review and update all environment variables
- [ ] Set strong database passwords
- [ ] Configure HTTPS/TLS certificates
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure log aggregation (ELK, Loki)
- [ ] Set up database backups
- [ ] Configure CI/CD pipeline
- [ ] Load test the system
- [ ] Security audit completed
- [ ] Disaster recovery plan in place

### Environment Configuration

Create production `.env`:

```bash
# Database
DATABASE_URL=postgresql://prod_user:STRONG_PASSWORD@prod-db-host:5432/production_db

# Application
DEBUG=False
PYTHONUNBUFFERED=1

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# API Configuration
API_KEY_SECRET=your_secret_key_min_32_chars
SECURITY_ALGORITHM=HS256

# External Services (if needed)
LOG_LEVEL=INFO
```

### Docker Deployment

#### 1. Build Production Images

```bash
# Build with production optimizations
docker build -t face-detection-backend:v1.0 \
  --build-arg ENV=production \
  -f backend/Dockerfile \
  backend/

docker build -t face-detection-frontend:v1.0 \
  --build-arg ENV=production \
  -f frontend/Dockerfile \
  frontend/
```

#### 2. Push to Registry

```bash
# Login to registry
docker login registry.example.com

# Tag images
docker tag face-detection-backend:v1.0 registry.example.com/backend:v1.0
docker tag face-detection-frontend:v1.0 registry.example.com/frontend:v1.0

# Push
docker push registry.example.com/backend:v1.0
docker push registry.example.com/frontend:v1.0
```

#### 3. Deploy with Docker Compose

```bash
# On production server
ssh deploy@production-server

# Create deployment directory
mkdir -p /opt/face-detection
cd /opt/face-detection

# Copy docker-compose.yml and .env
scp docker-compose.prod.yml deploy@production-server:/opt/face-detection/docker-compose.yml
scp .env.prod deploy@production-server:/opt/face-detection/.env

# Start services
docker-compose up -d

# Verify
docker-compose ps
curl https://yourdomain.com/api/health/
```

### Kubernetes Deployment (Advanced)

See `k8s/` directory for Kubernetes manifests:
- Deployments for backend and frontend
- Services for internal communication
- Ingress for external access
- ConfigMaps for configuration
- Secrets for sensitive data
- PersistentVolumes for database

```bash
# Deploy
kubectl apply -f k8s/

# Check status
kubectl get pods -n face-detection
kubectl logs -f deployment/backend -n face-detection
```

### Nginx Reverse Proxy Configuration

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/your_cert.crt;
    ssl_certificate_key /etc/ssl/private/your_key.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # API routes
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
    
    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
    }
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### Database Backup Strategy

```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="production_db"

# Daily backup
pg_dump \
    postgresql://user:password@db-host:5432/$DB_NAME \
    | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete

# Upload to S3
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://backup-bucket/
```

Schedule with cron:
```bash
0 2 * * * /usr/local/bin/backup_database.sh
```

### Monitoring & Alerting

#### Prometheus Scraping

```yaml
# Add to prometheus.yml
scrape_configs:
  - job_name: 'face-detection-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

#### Health Checks

```bash
# Script to monitor service health
#!/bin/bash

ENDPOINT="https://yourdomain.com/api/health/"
TIMEOUT=5

response=$(curl -s -w "\n%{http_code}" --connect-timeout $TIMEOUT $ENDPOINT)
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" != "200" ]; then
    echo "ALERT: API unhealthy (HTTP $http_code)"
    # Send alert to monitoring system
fi
```

Schedule every minute with cron.

### Logging Configuration

```python
# backend/app/logging_config.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
        }
        return json.dumps(log_obj)

# Configure
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(handler)
```

Aggregate logs with ELK Stack or similar.

### SSL/TLS Certificate

Use Let's Encrypt with Certbot:

```bash
# Initial certificate
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d app.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

Or with Docker:

```bash
docker run -it --rm \
  -v /opt/letsencrypt:/etc/letsencrypt \
  certbot/certbot certonly --standalone \
  -d yourdomain.com
```

### Performance Tuning

#### Database Connection Pool

```python
# backend/app/database.py
engine = create_engine(
    settings.database_url,
    pool_size=20,  # Increased for production
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
)
```

#### Uvicorn Workers

```bash
# Use multiple workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --log-level info
```

### Scalability

#### Horizontal Scaling

Deploy multiple backend instances:

```yaml
# docker-compose.yml
services:
  backend1:
    # ... config
  backend2:
    # ... config
  backend3:
    # ... config
  
  nginx:
    image: nginx:alpine
    # Load balance between backends
```

#### Caching Layer

Add Redis for caching hot ROI data:

```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:alpine
```

Update backend to use Redis:

```python
# backend/app/cache.py
import redis

cache = redis.Redis(host='redis', port=6379)

# Cache ROI queries
def get_latest_roi_cached(session_id):
    key = f"roi:latest:{session_id}"
    cached = cache.get(key)
    if cached:
        return json.loads(cached)
    # Query database...
```

### Disaster Recovery

**RTO (Recovery Time Objective)**: 1 hour
**RPO (Recovery Point Objective)**: 15 minutes

#### Backup Verification

```bash
# Weekly restore test
psql -h localhost -U restoreuser < /backups/postgresql/latest_backup.sql
# Run health checks
# Delete test database
```

#### Failover Plan

1. Primary database fails
2. Automatic failover to replica
3. Alert ops team
4. Investigate root cause
5. Restore from backup if needed

### Monitoring Dashboard

Create Grafana dashboard for:
- Request latency (p50, p95, p99)
- Error rate
- CPU/Memory usage
- Database connection pool
- Face detection success rate
- WebSocket concurrent connections

### Security Hardening

- [ ] Enable WAF (Web Application Firewall)
- [ ] Set up DDoS protection
- [ ] Configure rate limiting
- [ ] Enable database encryption at rest
- [ ] Use VPN for management access
- [ ] Regular security updates
- [ ] Penetration testing

### Compliance

- [ ] Data privacy (GDPR, CCPA)
- [ ] Audit logging
- [ ] Access control
- [ ] Encryption in transit and at rest
- [ ] Incident response plan

---

For detailed deployment support, contact your DevOps team or consult:
- Docker docs: https://docs.docker.com/
- Kubernetes docs: https://kubernetes.io/docs/
- Nginx docs: https://nginx.org/en/docs/
