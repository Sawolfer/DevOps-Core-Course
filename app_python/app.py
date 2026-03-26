import json
import logging
import os
import platform
import socket
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "devops-info-service",
        }

        for field in (
            "event",
            "method",
            "path",
            "status_code",
            "client_ip",
            "duration_ms",
            "host",
            "port",
        ):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=True)


def configure_logging() -> logging.Logger:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True

    return logging.getLogger("devops-info-service")


logger = configure_logging()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "Unknown"


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info(
        "application startup",
        extra={
            "event": "startup",
            "host": os.getenv("HOST", "0.0.0.0"),
            "port": int(os.getenv("PORT", 8000)),
        },
    )
    yield
    logger.info("application shutdown", extra={"event": "shutdown"})

# Fast API
app = FastAPI(
    title="DevOps Info Service",
    description="Lab 1 - System Monitoring Service",
    version="1.0.0",
    lifespan=lifespan,
)

# Prometheus metrics
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint", "status_code"],
)
HTTP_ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "Active HTTP requests",
    ["method", "endpoint", "status_code"],
)

DEVOPS_INFO_ENDPOINT_CALLS = Counter(
    "devops_info_endpoint_calls_total",
    "Endpoint calls",
    ["endpoint"],
)
DEVOPS_INFO_SYSTEM_COLLECTION_SECONDS = Histogram(
    "devops_info_system_collection_seconds",
    "System info collection time",
    ["endpoint"],
)
DEVOPS_INFO_UPTIME_SECONDS = Gauge(
    "devops_info_uptime_seconds",
    "Service uptime in seconds",
)

# Expose Prometheus metrics endpoint (no redirect).
@app.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

START_TIME = time.time()

start_time = datetime.now()

def get_uptime():
    delta = datetime.now() - start_time
    seconds = int(delta.total_seconds())
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return {
        'seconds': seconds,
        'human': f"{hours} hours, {minutes} minutes"
    }


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started_at = time.perf_counter()
    endpoint = request.url.path
    method = request.method

    in_progress_labels = (method, endpoint, "in_progress")
    HTTP_ACTIVE_REQUESTS.labels(*in_progress_labels).inc()

    status_code = "500"
    try:
        response = await call_next(request)
        status_code = str(response.status_code)
        return response
    finally:
        duration_seconds = time.perf_counter() - started_at
        duration_ms = round(duration_seconds * 1000, 2)

        HTTP_ACTIVE_REQUESTS.labels(*in_progress_labels).dec()
        HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).observe(duration_seconds)

        extra = {
            "event": "http_request",
            "method": request.method,
            "path": request.url.path,
            "status_code": int(status_code) if status_code.isdigit() else status_code,
            "client_ip": get_client_ip(request),
            "duration_ms": duration_ms,
        }

        if status_code.isdigit() and int(status_code) >= 400:
            logger.warning("request completed", extra=extra)
        else:
            logger.info("request completed", extra=extra)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not Found", "message": "Endpoint does not exist"}
    )

@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception):
    logger.exception(
        "unhandled exception",
        extra={
            "event": "request_error",
            "method": request.method,
            "path": request.url.path,
            "status_code": 500,
            "client_ip": get_client_ip(request),
        },
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": "Something went wrong"}
    )

@app.get("/")
async def root(request: Request):
    """
    Returns comprehensive system and service information.
    """
    DEVOPS_INFO_ENDPOINT_CALLS.labels(endpoint="/").inc()
    collection_started_at = time.perf_counter()
    uptime = get_uptime()
    DEVOPS_INFO_UPTIME_SECONDS.set(uptime["seconds"])
    
    data = {
        "service": {
            "name": "devops-info-service",
            "version": "1.0.0",
            "description": "DevOps course info service",
            "framework": "FastAPI"
        },
        "system": {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "cpu_count": os.cpu_count() or "Unknown",
            "python_version": platform.python_version()
        },
        "runtime": {
            "uptime_seconds": uptime["seconds"],
            "uptime_human": uptime["human"],
            "current_time": utc_now_iso(),
            "timezone": "UTC"
        },
        "request": {
            "client_ip": get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
            "method": request.method,
            "path": request.url.path
        },
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Service information"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/metrics", "method": "GET", "description": "Prometheus metrics"},
        ]
    }

    DEVOPS_INFO_SYSTEM_COLLECTION_SECONDS.labels(endpoint="/").observe(
        time.perf_counter() - collection_started_at
    )
    return data

@app.get("/health")
async def health_check():
    """
    Simple health check for Kubernetes probes.
    """
    DEVOPS_INFO_ENDPOINT_CALLS.labels(endpoint="/health").inc()
    uptime = get_uptime()
    DEVOPS_INFO_UPTIME_SECONDS.set(uptime["seconds"])
    return {
        "status": "healthy",
        "timestamp": utc_now_iso(),
        "uptime_seconds": uptime["seconds"]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(
        "starting server",
        extra={"event": "bootstrap", "host": host, "port": port},
    )
    uvicorn.run(app, host=host, port=port, access_log=False, log_config=None)