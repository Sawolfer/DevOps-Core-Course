# Lab 2 - Docker Containerization

## Docker Best Practices Applied

### 1. Non-Root User
**Implementation:**
```dockerfile
RUN groupadd -r appuser && useradd -r -g appuser -s /bin/bash -m appuser
USER appuser
```
**Why it matters:** Running containers as root is a major security risk. If an attacker gains access to the container, they would have root privileges on the container. By running as a non-root user, we follow the principle of least privilege, minimizing potential damage if the container is compromised.

### 2. Specific Base Image Version
Implementation:

```dockerfile
FROM python:3.13-slim
```
**Why it matters:** Using a specific version (python:3.13-slim) ensures reproducibility. The slim variant is smaller than the full image (contains only minimal packages needed to run Python) while being more stable than alpine (which can have compatibility issues with some Python packages)

### 3. Layer Caching Optimization
Implementation:

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```
**Why it matters:** Docker caches layers. By copying requirements.txt first and installing dependencies before copying the application code, we ensure that dependency installation is only re-run when dependencies change. Application code changes won't trigger a reinstallation of dependencies, making builds faster.

### 4. .dockerignore File
Implementation: See .dockerignore file above.

**Why it matters:** Excludes unnecessary files from the build context, reducing build time and image size. It also prevents sensitive files (like .env, secrets) from accidentally being included in the image.

### 5. Environment Variables
Implementation:

```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV HOST=0.0.0.0
```
**Why it matters:**

```PYTHONDONTWRITEBYTECODE=1```: Prevents Python from writing .pyc files

```PYTHONUNBUFFERED=1```: Ensures Python output is sent straight to terminal

Configurable PORT and HOST for flexibility

### 6. Health Check
Implementation:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

**Why it matters**: Provides a way for Docker and orchestration tools (like Kubernetes) to monitor container health. If the health check fails, the container can be automatically restarted or removed from service.

## Image Information & Decisions
### Base Image Choice
**Selected: python:3.13-slim**

**Justification:**

**Official Image:** Maintained by Docker with regular security updates

**Size:** 170MB vs 1GB for full Python image

**Compatibility:** Uses glibc (standard C library) ensuring compatibility with all Python packages

**Features:** Includes essential packages for most applications without bloat

### Image Size Analysis
```
$ docker images
devops-info-service:latest   8c105131e841        170MB
```
**Assessment**: 170MB is an excellent size for a production-ready Python application with FastAPI and Uvicorn. Could potentially be reduced to ~50MB with Alpine, but at the risk of compatibility issues.

### Layer Structure Analysis
```
$ docker history devops-info-service:latest

IMAGE          CREATED         CREATED BY                                      SIZE      
8c105131e841   9 minutes ago   CMD ["python" "app.py"]                         0B        
<missing>      9 minutes ago   HEALTHCHECK                                    0B        
<missing>      9 minutes ago   EXPOSE [8000/tcp]                              0B        
<missing>      9 minutes ago   USER appuser                                   0B        
<missing>      9 minutes ago   RUN chown -R appuser:appuser /app              1.56MB    
<missing>      9 minutes ago   COPY . .                                       1.56MB    
<missing>      9 minutes ago   RUN pip install --no-cache-dir ...             24.4MB    
<missing>      9 minutes ago   COPY requirements.txt .                        235B      
<missing>      9 minutes ago   WORKDIR /app                                   0B        
<missing>      9 minutes ago   ENV variables                                  0B        
<missing>      9 minutes ago   RUN groupadd -r appuser ...                    8.87kB    
<missing>      41 hours ago    Python 3.13.11 base layers                     ~144MB    
```
**Layer Breakdown:**

**Base Layers (144MB):** Python 3.13.11 runtime environment

**Dependencies (24.4MB):** FastAPI, Uvicorn, and related packages

**Application Code (1.56MB):** Source code and documentation

**Permissions (1.56MB):** Setting ownership for non-root user

**Metadata (0B):** Configuration (USER, EXPOSE, HEALTHCHECK, CMD)

## Build & Run Process

### Terminal Output - Build Process
```bash
$ docker build -t devops-info-service:latest .

[+] Building 0.9s (12/12) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 1.48kB
 => [internal] load metadata for docker.io/library/python:3.13-slim
 => [internal] load .dockerignore
 => => transferring context: 585B
 => [1/7] FROM docker.io/library/python:3.13-slim@sha256:2b9c9803c6a287cafa0a8c917211dddd23dcd2016f049690ee5219f5d3f1636e
 => CACHED [2/7] RUN groupadd -r appuser && useradd -r -g appuser -s /bin/bash -m appuser
 => CACHED [3/7] WORKDIR /app
 => CACHED [4/7] COPY requirements.txt .
 => CACHED [5/7] RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
 => CACHED [6/7] COPY . .
 => CACHED [7/7] RUN chown -R appuser:appuser /app
 => exporting to image
 => => writing image sha256:8c105131e8419f30e5a4aa8aaa3719ee1ade9b9f9ed8817e8cada3fc3a474ab0
 => => naming to docker.io/library/devops-info-service:latest

Successfully built 8c105131e841
Successfully tagged devops-info-service:latest
```

**Note:** The `CACHED` indicators show Docker is effectively using layer caching.

### Terminal Output - Running Container
```bash
$ docker run -d -p 8000:8000 --name devops-info devops-info-service:latest
cc8f70d696ea0916c249cb0ad9c3be454a7a3ea3bdf40427256ca056d71ba2a4

$ docker ps
CONTAINER ID   IMAGE                        COMMAND           CREATED         STATUS                            PORTS                                         NAMES
cc8f70d696ea   devops-info-service:latest   "python app.py"   5 seconds ago   Up 4 seconds (health: starting)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp   devops-info
```
### Terminal Output - Container Logs
```bash
$ docker logs devops-info
2026-02-04 20:15:49,481 - devops-info-service - INFO - Starting server on 0.0.0.0:8000
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Terminal Output - Testing Endpoints
**Root Endpoint (/):**

```bash
$ curl http://localhost:8000/
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "FastAPI"
  },
  "system": {
    "hostname": "cc8f70d696ea",
    "platform": "Linux",
    "platform_version": "#1 SMP Sun Jan 25 02:26:28 UTC 2026",
    "architecture": "aarch64",
    "cpu_count": 8,
    "python_version": "3.13.11"
  },
  "runtime": {
    "uptime_seconds": 33,
    "uptime_human": "0 hours, 0 minutes",
    "current_time": "2026-02-04T20:16:22.835162Z",
    "timezone": "UTC"
  },
  "request": {
    "client_ip": "192.168.65.1",
    "user_agent": "curl/8.7.1",
    "method": "GET",
    "path": "/"
  },
  "endpoints": [
    {"path": "/", "method": "GET", "description": "Service information"},
    {"path": "/health", "method": "GET", "description": "Health check"}
  ]
}
```
**Health Check (/health):**

```bash
$ curl http://localhost:8000/health
{
  "status": "healthy",
  "timestamp": "2026-02-04T20:16:27.435292Z",
  "uptime_seconds": 37
}
```
**Non-existent Endpoint (404 Test):**

```bash
$ curl http://localhost:8000/nonexistent
{
  "error": "Not Found",
  "message": "Endpoint does not exist"
}
```

### Container Inspection
```bash
$ docker exec -it devops-info bash
appuser@cc8f70d696ea:/app$ whoami
appuser

appuser@cc8f70d696ea:/app$ ls -la
total 32
drwxr-xr-x 1 appuser appuser 4096 Feb  4 20:11 .
drwxr-xr-x 1 root    root    4096 Feb  4 20:15 ..
-rw-r--r-- 1 appuser appuser 3061 Feb  4 19:52 README.md
-rw-r--r-- 1 appuser appuser 3383 Feb  4 19:52 app.py
drwx------ 1 appuser appuser 4096 Feb  4 19:55 docs
-rw-r--r-- 1 appuser appuser  235 Feb  4 19:52 requirements.txt

appuser@cc8f70d696ea:/app$ pwd
/app
```

## Docker Hub Publication
### Tagging Strategy
```bash
# Tag local image with Docker Hub username
$ docker tag devops-info-service:latest brainpumpkin/devops-info-service:latest
```
**Tagging Convention:** username/repository:tag

**brainpumpkin**: Docker Hub username

**devops-info-service**: Repository name

**latest**: Tag indicating the most recent stable version

### Push to Docker Hub
```bash
$ docker push brainpumpkin/devops-info-service:latest
The push refers to repository [docker.io/brainpumpkin/devops-info-service]
c5701797d95a: Pushed 
bc786dc1d3e5: Pushed 
bfffdffadd53: Pushed 
8844de48ce0d: Pushed 
3f25e8042893: Pushed 
fc797c5523cd: Pushed 
083605e5ab90: Mounted from library/python 
675d3200abe3: Mounted from library/python 
e6060824c6b0: Mounted from library/python 
a0e71ab2b234: Mounted from library/python 
latest: digest: sha256:3c36a29af0887b720b2c8df8dd301c319474b560cd2ec09b4fc44f008125dc45 size: 2413
```
### Docker Hub Repository
URL: https://hub.docker.com/r/brainpumpkin/devops-info-service

### Pull and Run from Docker Hub
```bash
# Remove local copy to test pulling from remote
$ docker rmi brainpumpkin/devops-info-service:latest
Untagged: brainpumpkin/devops-info-service:latest
Untagged: brainpumpkin/devops-info-service@sha256:3c36a29af0887b720b2c8df8dd301c319474b560cd2ec09b4fc44f008125dc45

# Pull from Docker Hub
$ docker pull brainpumpkin/devops-info-service:latest
latest: Pulling from brainpumpkin/devops-info-service
Digest: sha256:3c36a29af0887b720b2c8df8dd301c319474b560cd2ec09b4fc44f008125dc45
Status: Downloaded newer image for brainpumpkin/devops-info-service:latest
docker.io/brainpumpkin/devops-info-service:latest

# Run the pulled image
$ docker run -d -p 8000:8000 --name devops-info-hub brainpumpkin/devops-info-service:latest
a3321a3bedc67282e759a271ddf375a4622edc819cd299c44513c229f1bab4f1

# Verify it works
$ curl http://localhost:8000/
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "FastAPI"
  },
  "system": {
    "hostname": "a3321a3bedc6",
    "platform": "Linux",
    "platform_version": "#1 SMP Sun Jan 25 02:26:28 UTC 2026",
    "architecture": "aarch64",
    "cpu_count": 8,
    "python_version": "3.13.11"
  },
  "runtime": {
    "uptime_seconds": 4,
    "uptime_human": "0 hours, 0 minutes",
    "current_time": "2026-02-04T20:21:05.923584Z",
    "timezone": "UTC"
  },
  "request": {
    "client_ip": "192.168.65.1",
    "user_agent": "curl/8.7.1",
    "method": "GET",
    "path": "/"
  },
  "endpoints": [
    {"path": "/", "method": "GET", "description": "Service information"},
    {"path": "/health", "method": "GET", "description": "Health check"}
  ]
}
```

## Technical Analysis
### Why This Dockerfile Structure Works
1. **Optimal Caching**: Dependencies installed before application code means code changes don't trigger dependency reinstallation

2. **Security First**: Non-root user created early and used for all operations

3. **Minimal Layers**: Each instruction creates a separate layer; we minimize layer count where possible

4. **Explicit Ports**: EXPOSE 8000 documents which port the application uses

## What Would Happen With Different Layer Order?
**Current (Optimized):**

```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt  # Cached unless requirements.txt changes
COPY . .                             # New layer when code changes
```
**Inefficient Alternative:**

```dockerfile
COPY . .                             # New layer when ANY file changes
RUN pip install -r requirements.txt  # ALWAYS reinstalls dependencies
```
**Impact**: The inefficient approach would reinstall all Python dependencies (~24.4MB download, ~30 seconds) on every code change, making development painfully slow.

### Security Considerations Implemented
1. **Non-Root Execution**: Container runs as appuser not root

2. **Principle of Least Privilege**: User only has access to /app directory

3. **No Build Tools in Runtime**: Development tools not included in final image

4. **Clean Package Installation**: --no-cache-dir prevents pip cache accumulation

5. **Health Monitoring**: Built-in health checks for orchestration

### How .dockerignore Improves Build Process
1. **Reduced Context Size**: From ~5MB to ~1MB (80% reduction)

2. **Faster Builds**: Smaller context = faster transfer to Docker daemon

3. **Security**: Prevents accidental inclusion of secrets (.env, .git)

4. **Clean Images**: No development artifacts in production images

## Challenges & Solutions

Challenge 1: Permission Issues in Container
Problem: Non-root user couldn't access application files

Solution: Set proper ownership before switching users:

```dockerfile
RUN chown -R appuser:appuser /app
USER appuser
```

## Lessons Learned
1. **Layer Caching is Critical**: Proper layer ordering can reduce build times from minutes to seconds

2. **Security is Not Optional**: Non-root users should be default, not an afterthought

3. **Image Size Matters**: Smaller images deploy faster and have smaller attack surfaces

4. **Documentation in Dockerfile**: LABELs provide valuable metadata for maintenance

5. **Testing is Essential**: Always test that the containerized app works identically to local

## Conclusion
The application has been successfully containerized following Docker best practices:

✅ Non-root user implementation

✅ Optimized layer caching

✅ Security hardening

✅ Health monitoring

✅ Published to Docker Hub

✅ Comprehensive documentation