# DevOps Info Service

A simple web service that provides comprehensive information about itself and its runtime environment. Built for the DevOps course Lab 1.

## Overview

This service exposes two HTTP endpoints:
- `/` - Returns detailed service, system, runtime, and request information
- `/health` - Returns health status (for monitoring and Kubernetes probes)

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

**Examples:**
```bash
# Run on port 9000
PORT=9000 python app.py

# Run on localhost only, port 3000
HOST=127.0.0.1 PORT=3000 python app.py


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
## Testing

### Using browser
Simply open http://localhost:8000 in your browser.

### Using curl
```bash
# Main endpoint
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health

# Pretty print with jq (if installed)
curl http://localhost:8000/ | jq
```

## Technologies Used
FastAPI 0.115.0 - Modern Python web framework

Uvicorn 0.32.0 - ASGI server

Python 3.11+ - Programming language