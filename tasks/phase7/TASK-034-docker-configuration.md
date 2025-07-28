# TASK-034: Docker Configuration

## Task Information
- **ID**: TASK-034
- **Phase**: 7 - Documentation & Deployment
- **Estimate**: 60 minutes
- **Dependencies**: TASK-031
- **Status**: 🔴 Backlog

## Description
Create Docker configuration for containerizing the MindTube application, including Dockerfile, docker-compose setup, and deployment configurations for both development and production environments.

## Acceptance Criteria
- [ ] Create optimized Dockerfile
- [ ] Set up docker-compose for development
- [ ] Create production docker-compose
- [ ] Add health checks
- [ ] Configure environment variables
- [ ] Set up volume mounts
- [ ] Add Docker documentation
- [ ] Test container builds and runs

## Implementation Details

### Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash mindtube
USER mindtube
WORKDIR /home/mindtube

# Copy requirements first for better caching
COPY --chown=mindtube:mindtube requirements.txt .
COPY --chown=mindtube:mindtube requirements-dev.txt .

# Install Python dependencies
RUN pip install --user -r requirements.txt

# Development stage
FROM base as development
RUN pip install --user -r requirements-dev.txt
COPY --chown=mindtube:mindtube . .
RUN pip install --user -e .
EXPOSE 8000
CMD ["python", "-m", "mindtube.api.main", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production
COPY --chown=mindtube:mindtube . .
RUN pip install --user .

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

EXPOSE 8000
CMD ["python", "-m", "mindtube.api.main", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Multi-stage Dockerfile (Optimized)
```dockerfile
# Dockerfile.optimized
# Build stage
FROM python:3.11-slim as builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source and install package
COPY . .
RUN pip install .

# Runtime stage
FROM python:3.11-slim as runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash mindtube

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set up application
USER mindtube
WORKDIR /home/mindtube

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

EXPOSE 8000
CMD ["mindtube", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

### Development Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  mindtube:
    build:
      context: .
      target: development
    ports:
      - "8000:8000"
    volumes:
      - .:/home/mindtube
      - mindtube_cache:/home/mindtube/.cache
    environment:
      - ENVIRONMENT=development
      - LOG_LEVEL=debug
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  redis-commander:
    image: rediscommander/redis-commander:latest
    environment:
      - REDIS_HOSTS=local:redis:6379
    ports:
      - "8081:8081"
    depends_on:
      - redis
    profiles:
      - tools

volumes:
  mindtube_cache:
  redis_data:
```

### Production Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mindtube:
    build:
      context: .
      target: production
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=info
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379/0
      - ENABLE_RATE_LIMITING=true
    depends_on:
      - redis
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - mindtube
    restart: unless-stopped

volumes:
  redis_data:
```

### Nginx Configuration
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream mindtube {
        server mindtube:8000;
    }

    server {
        listen 80;
        server_name localhost;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name localhost;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        # API routes
        location /api/ {
            proxy_pass http://mindtube;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket support
        location /api/v1/ws {
            proxy_pass http://mindtube;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            proxy_pass http://mindtube/api/v1/health;
        }
    }
}
```

### Docker Ignore
```gitignore
# .dockerignore
.git
.gitignore
README.md
Dockerfile*
docker-compose*.yml
.dockerignore
.pytest_cache
.coverage
.mypy_cache
.ruff_cache
__pycache__
*.pyc
*.pyo
*.pyd
.env
.venv
venv/
.DS_Store
*.log
tests/
docs/
.github/
```

### Environment Configuration
```bash
# .env.example
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2023-12-01-preview
AZURE_OPENAI_MODEL=gpt-4

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=info
DEBUG=false

# Database Configuration
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENABLE_RATE_LIMITING=true
CORS_ORIGINS=["http://localhost:3000"]

# Security
SECRET_KEY=your-secret-key
API_KEY=your-api-key
```

### Docker Scripts
```bash
#!/bin/bash
# scripts/docker-build.sh

set -e

echo "Building MindTube Docker images..."

# Build development image
docker build -t mindtube:dev --target development .

# Build production image
docker build -t mindtube:prod --target production .

echo "Build complete!"
echo "Development image: mindtube:dev"
echo "Production image: mindtube:prod"
```

```bash
#!/bin/bash
# scripts/docker-run.sh

set -e

MODE=${1:-dev}

if [ "$MODE" = "prod" ]; then
    echo "Starting production environment..."
    docker-compose -f docker-compose.prod.yml up -d
else
    echo "Starting development environment..."
    docker-compose up -d
fi

echo "MindTube is starting..."
echo "API will be available at: http://localhost:8000"
echo "Health check: http://localhost:8000/api/v1/health"

if [ "$MODE" = "dev" ]; then
    echo "Redis Commander: http://localhost:8081"
fi
```

### Makefile Integration
```makefile
# Add to existing Makefile

# Docker targets
.PHONY: docker-build docker-run docker-stop docker-clean

docker-build:
	@echo "Building Docker images..."
	docker build -t mindtube:dev --target development .
	docker build -t mindtube:prod --target production .

docker-run:
	@echo "Starting development environment..."
	docker-compose up -d

docker-run-prod:
	@echo "Starting production environment..."
	docker-compose -f docker-compose.prod.yml up -d

docker-stop:
	@echo "Stopping containers..."
	docker-compose down
	docker-compose -f docker-compose.prod.yml down

docker-clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down -v
	docker system prune -f

docker-logs:
	docker-compose logs -f mindtube

docker-shell:
	docker-compose exec mindtube bash
```

### Documentation
```markdown
# docs/deployment/docker.md

# Docker Deployment Guide

## Quick Start

### Development
```bash
# Build and run development environment
make docker-build
make docker-run

# View logs
make docker-logs

# Access container shell
make docker-shell
```

### Production
```bash
# Build production image
docker build -t mindtube:prod --target production .

# Run production environment
make docker-run-prod
```

## Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your configuration
```

### SSL Certificates
For production HTTPS, place certificates in `ssl/` directory:
- `ssl/cert.pem` - SSL certificate
- `ssl/key.pem` - Private key

## Monitoring

### Health Checks
```bash
# Check application health
curl http://localhost:8000/api/v1/health

# Check container health
docker-compose ps
```

### Logs
```bash
# View application logs
docker-compose logs -f mindtube

# View all logs
docker-compose logs -f
```

## Scaling

### Horizontal Scaling
```yaml
# In docker-compose.prod.yml
services:
  mindtube:
    deploy:
      replicas: 4  # Scale to 4 instances
```

### Resource Limits
```yaml
services:
  mindtube:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

## Troubleshooting

### Common Issues
1. **Port conflicts**: Change ports in docker-compose.yml
2. **Memory issues**: Increase Docker memory limits
3. **Permission errors**: Check file ownership and permissions
4. **Network issues**: Verify Docker network configuration
```

## Testing

### Docker Tests
```bash
# scripts/test-docker.sh
#!/bin/bash

set -e

echo "Testing Docker configuration..."

# Build images
docker build -t mindtube:test --target development .

# Test container startup
docker run --rm -d --name mindtube-test -p 8080:8000 mindtube:test

# Wait for startup
sleep 10

# Test health endpoint
if curl -f http://localhost:8080/api/v1/health; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi

# Cleanup
docker stop mindtube-test

echo "✅ Docker tests passed"
```

## Verification Steps
1. [ ] Dockerfile builds successfully
2. [ ] Development compose starts correctly
3. [ ] Production compose starts correctly
4. [ ] Health checks work
5. [ ] Environment variables are configured
6. [ ] Volumes persist data correctly
7. [ ] Nginx proxy works (production)
8. [ ] SSL configuration works (production)

## Dependencies
- TASK-031 (Security testing) for security configurations
- Docker and Docker Compose installed
- SSL certificates for production HTTPS

## Notes
- Use multi-stage builds for optimized images
- Implement proper health checks
- Configure resource limits for production
- Use secrets management for sensitive data
- Consider using Docker Swarm or Kubernetes for orchestration