# DevOps Info Service

A simple web service that provides comprehensive information about itself and its runtime environment. Built for the DevOps course Lab 1.

## Overview

This service exposes HTTP endpoints:
- `/` - Returns detailed service, system, runtime, and request information
- `/health` - Returns health status (for monitoring and Kubernetes probes)
- `/visits` - Returns persisted visits counter
- `/metrics` - Exposes Prometheus metrics (for scraping)

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

## Installation

1. Clone the repository and navigate to the application directory:
```bash
cd app_python
```
2. Create and activate a virtual environment (optional):
```bash 
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

**Default configuration (localhost:8000)**
```bash 
python app.py
```
**Custom port**
```bash
PORT=9000 python app.py
```
**Custom host and port**
```bash
HOST=127.0.0.1 PORT=3000 python app.py
```
The service will start and log:
```
INFO: Starting server on 0.0.0.0:8000
INFO: Application startup complete.
```

## Configuration

The application can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host address (use 127.0.0.1 for localhost only) |
| `PORT` | `8000` | Server port number |
| `VISITS_FILE` | `data/visits` | Path to file with persisted visits counter |

**Examples:**
```bash
# Run on port 9000
PORT=9000 python app.py

# Run on localhost only, port 3000
HOST=127.0.0.1 PORT=3000 python app.py
```

## Visits Persistence

Each request to `/` increments a counter stored in `VISITS_FILE`.

- `GET /` increments and returns current value under `stats.visits`
- `GET /visits` returns current counter without incrementing

**Example:**
```bash
curl http://localhost:8000/visits
```

```json
{
  "visits": 3
}
```


## API Endpoints
**GET /**

Returns comprehensive service and system information.

*Response example*
```json
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "FastAPI"
  },
  "system": {
    "hostname": "my-laptop",
    "platform": "Linux",
    "platform_version": "Ubuntu 24.04",
    "architecture": "x86_64",
    "cpu_count": 8,
    "python_version": "3.13.1"
  },
  "runtime": {
    "uptime_seconds": 3600,
    "uptime_human": "1 hours, 0 minutes, 0 seconds",
    "current_time": "2026-01-28T07:30:00.000Z",
    "timezone": "UTC"
  },
  "request": {
    "client_ip": "127.0.0.1",
    "user_agent": "Mozilla/5.0...",
    "method": "GET",
    "path": "/"
  },
  "endpoints": [
    {"path": "/", "method": "GET", "description": "Service information"},
    {"path": "/health", "method": "GET", "description": "Health check"}
  ]
}
```
**GET /health**

Simple health check endpoint for monitoring.

*Response example*

```json
{
  "status": "healthy",
  "timestamp": "2026-01-28T07:30:00.000Z",
  "uptime_seconds": 3600
}
```

**GET /visits**

Returns current persisted visits counter.

*Response example*

```json
{
  "visits": 7
}
```

**GET /metrics**

Prometheus-compatible metrics endpoint.

*Example*
```bash
curl http://localhost:8000/metrics
```
## Testing

### Using browser
Simply open http://localhost:8000 in your browser.

### Using curl
```bash
# Main endpoint
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health

# Prometheus metrics
curl http://localhost:8000/metrics

# Pretty print with jq (if installed)
curl http://localhost:8000/ | jq
```

## Technologies Used
FastAPI 0.115.0 - Modern Python web framework

Uvicorn 0.32.0 - ASGI server

Python 3.11+ - Programming language

## Docker Containerization

This application is containerized using Docker for consistent deployment.

### Quick Start
```bash
# Build locally
docker build -t devops-info-service:latest .

# Run locally
docker run -d -p 8000:8000 devops-info-service:latest

# Or pull from Docker Hub
docker pull brainpumpkin/devops-info-service:latest
docker run -d -p 8000:8000 brainpumpkin/devops-info-service:latest
```

### Persist Visits Counter with Docker Compose

From [monitoring/docker-compose.yml](../monitoring/docker-compose.yml), service `app-python` mounts `../app_python/data:/app/data` and sets `VISITS_FILE=/app/data/visits`.

Validation flow:
```bash
cd monitoring
docker compose up -d app-python

curl http://localhost:8000/
curl http://localhost:8000/
curl http://localhost:8000/visits

cat ../app_python/data/visits
docker compose restart app-python
curl http://localhost:8000/visits
```

The value after restart should continue from the previous counter value.
## Docker Hub
Repository: https://hub.docker.com/r/brainpumpkin/devops-info-service

### Pull Command:

```bash
docker pull brainpumpkin/devops-info-service:latest
```
### Useful Commands
```bash
# View running containers
docker ps

# View logs
docker logs devops-info

# Stop container
docker stop devops-info

# Enter container shell
docker exec -it devops-info bash

# Check health status
docker inspect --format='{{.State.Health.Status}}' devops-info
```

# DevOps Info Service

![Python CI/CD Pipeline](https://github.com/Sawolfer/DevOps-Core-Course/workflows/Python%20CI%2FCD%20Pipeline/badge.svg?branch=lab03)