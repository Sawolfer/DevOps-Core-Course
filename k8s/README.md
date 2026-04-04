# Lab 9 — Kubernetes Fundamentals

This document contains implementation and evidence for all required Lab 9 tasks and bonus tasks.

## 1. Architecture Overview

Chosen local cluster tool: kind.

Why kind:
- Lightweight and fast startup on macOS.
- Works well with Docker-based local workflows.
- Common choice for CI/CD-like local testing.

Deployment architecture:

```text
Client (curl/browser)
       |
       | kubectl port-forward service/devops-info-service 8080:80
       v
NodePort Service (port 80 -> targetPort http)
       |
       v
Deployment devops-info-service (replicas: 5 during scaling demo)
       |
       +--> Pod 1 (FastAPI, /health, /metrics)
       +--> Pod 2 (FastAPI, /health, /metrics)
       +--> Pod 3 (FastAPI, /health, /metrics)
       +--> Pod 4 (FastAPI, /health, /metrics)
       +--> Pod 5 (FastAPI, /health, /metrics)
```

Resource allocation strategy:
- requests: cpu 100m, memory 128Mi.
- limits: cpu 300m, memory 256Mi.
- This gives predictable scheduling while preventing noisy-neighbor behavior.

## 2. Manifest Files

### deployment.yml
File: k8s/deployment.yml

Key choices:
- `replicas: 3` as baseline, then scaled to 5 in operations.
- Rolling update strategy with `maxUnavailable: 0` and `maxSurge: 1` to maintain availability.
- Liveness and readiness probes on `GET /health`.
- `imagePullPolicy: IfNotPresent` for local kind image workflow.
- Explicit resource requests/limits.
- Labels (`app`, `component`) for clean selection and organization.

### service.yml
File: k8s/service.yml

Key choices:
- Service type `NodePort` (required by lab for local exposure).
- Service port 80 -> container named port `http` (8000).
- Selector matches deployment label: `app=devops-info-service`.

## 3. Deployment Evidence

### Task 1: Local Kubernetes Setup

Cluster creation:

```bash
kind create cluster --name lab09
```

Output:
```text
Creating cluster "lab09" ...
✓ Ensuring node image (kindest/node:v1.35.0)
✓ Preparing nodes
✓ Writing configuration
✓ Starting control-plane
✓ Installing CNI
✓ Installing StorageClass
Set kubectl context to "kind-lab09"
```

Cluster info:

```bash
kubectl cluster-info
```

Output:
```text
Kubernetes control plane is running at https://127.0.0.1:61363
CoreDNS is running at https://127.0.0.1:61363/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

Nodes:

```bash
kubectl get nodes -o wide
```

Output:
```text
NAME                  STATUS   ROLES           AGE   VERSION   INTERNAL-IP   OS-IMAGE                         CONTAINER-RUNTIME
lab09-control-plane   Ready    control-plane   92s   v1.35.0   172.19.0.2    Debian GNU/Linux 12 (bookworm)   containerd://2.2.0
```

Namespaces:

```bash
kubectl get namespaces
```

Output:
```text
NAME                 STATUS   AGE
default              Active   5m39s
kube-node-lease      Active   5m39s
kube-public          Active   5m39s
kube-system          Active   5m39s
local-path-storage   Active   5m35s
```

### Task 2 + Task 3: Deployment and Service

Apply manifests:

```bash
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl rollout status deployment/devops-info-service
```

Output:
```text
deployment.apps/devops-info-service created
service/devops-info-service created
deployment "devops-info-service" successfully rolled out
```

Detailed state:

```bash
kubectl get pods,svc,deploy -o wide
```

Output (excerpt):
```text
pod/devops-info-service-6775b96f5d-gm6bv   1/1 Running
pod/devops-info-service-6775b96f5d-hjqwr   1/1 Running
pod/devops-info-service-6775b96f5d-ng6c7   1/1 Running
service/devops-info-service                NodePort   80:30080/TCP
deployment.apps/devops-info-service        3/3 ready, image devops-info-service:v1
```

Service connectivity check (port-forward method):

```bash
kubectl port-forward service/devops-info-service 8080:80
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/
curl http://127.0.0.1:8080/metrics
```

Output excerpts:
```json
{"status":"healthy","timestamp":"2026-03-26T17:58:48.074802Z","uptime_seconds":145}
```

```text
{"service":{"name":"devops-info-service","version":"1.0.0","description":"DevOps course info service","framework":"FastAPI"}, ... }
```

```text
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
...
```

## 4. Operations Performed

### Scaling to 5 replicas

```bash
kubectl scale deployment/devops-info-service --replicas=5
kubectl rollout status deployment/devops-info-service
kubectl get deploy devops-info-service
```

Output:
```text
deployment.apps/devops-info-service scaled
deployment "devops-info-service" successfully rolled out
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE
devops-info-service   5/5     5            5           31s
```

### Rolling update

```bash
kubectl set image deployment/devops-info-service devops-info-service=devops-info-service:v2
kubectl rollout status deployment/devops-info-service
kubectl rollout history deployment/devops-info-service
```

Output:
```text
deployment.apps/devops-info-service image updated
deployment "devops-info-service" successfully rolled out
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

### Rollback

```bash
kubectl rollout undo deployment/devops-info-service
kubectl rollout status deployment/devops-info-service
kubectl rollout history deployment/devops-info-service
```

Output:
```text
deployment.apps/devops-info-service rolled back
deployment "devops-info-service" successfully rolled out
REVISION  CHANGE-CAUSE
2         <none>
3         <none>
```

Current image after rollback:

```bash
kubectl get deploy devops-info-service -o wide
```

Output:
```text
IMAGES
... devops-info-service:v1
```

## 5. Production Considerations

Health checks:
- Liveness probe on `/health` restarts unhealthy containers.
- Readiness probe on `/health` prevents traffic to not-ready pods.
- Using both reduces user-facing errors during startup or partial failures.

Resource limits rationale:
- Requests guarantee minimum resources for scheduling.
- Limits cap max consumption to keep node stable.
- Chosen values are conservative for a small FastAPI service.

How to improve for production:
- Use dedicated readiness endpoint (`/ready`) with dependency checks.
- Add HPA (HorizontalPodAutoscaler) based on CPU/request metrics.
- Add PodDisruptionBudget and anti-affinity for better resilience.
- Add Ingress/Gateway with TLS and rate limiting.
- Use pinned digest images and vulnerability scanning in CI.

Monitoring/observability strategy:
- Scrape `/metrics` with Prometheus.
- Add Grafana dashboard for RED metrics.
- Correlate logs (Loki) and metrics for incident analysis.

## 6. Challenges and Solutions

1. Challenge: Docker daemon was not running.
- Symptom: cannot connect to Docker socket.
- Fix: started Docker Desktop and re-ran commands.

2. Challenge: Docker Hub image had no linux/arm64 manifest.
- Symptom: pull failed on Apple Silicon.
- Fix: built local image from `app_python/` and loaded it into kind with `kind load docker-image`.

3. Challenge: NodePort access in kind can be environment-dependent.
- Fix: used `kubectl port-forward` for deterministic local verification.

Main learnings:
- Kubernetes declarative workflow is practical for repeatable deployments.
- Probes and rollout strategy significantly improve update safety.
- Rolling updates and rollback are straightforward and observable with kubectl.

## Command Summary

```bash
# Tooling and cluster
kind create cluster --name lab09
kubectl cluster-info
kubectl get nodes -o wide

# Build and load image
docker build -t devops-info-service:v1 ./app_python
docker tag devops-info-service:v1 devops-info-service:v2
kind load docker-image devops-info-service:v1 --name lab09
kind load docker-image devops-info-service:v2 --name lab09

# Deploy
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl rollout status deployment/devops-info-service

# Validate
kubectl get all
kubectl describe deployment devops-info-service
kubectl port-forward service/devops-info-service 8080:80
curl http://127.0.0.1:8080/health

# Task 4 operations
kubectl scale deployment/devops-info-service --replicas=5
kubectl set image deployment/devops-info-service devops-info-service=devops-info-service:v2
kubectl rollout undo deployment/devops-info-service
```

## 7. Bonus Task — Ingress with TLS

### Bonus Manifests

Created files:
- `k8s/bonus-app1-service.yml`
- `k8s/bonus-app2-deployment.yml`
- `k8s/bonus-app2-service.yml`
- `k8s/bonus-ingress.yml`

What was implemented:
- Second application deployed as `devops-info-service-app2` with separate labels and service.
- Ingress controller (NGINX) installed in `ingress-nginx` namespace.
- Path routing configured:
       - `/app1` -> `app1-service`
       - `/app2` -> `app2-service`
- TLS enabled on host `local.example.com` using self-signed certificate in secret `bonus-local-tls`.

### Bonus Evidence

Ingress controller installation:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl -n ingress-nginx rollout status deployment/ingress-nginx-controller
```

Output:
```text
namespace/ingress-nginx created
...
deployment "ingress-nginx-controller" successfully rolled out
```

Deploy bonus workloads:

```bash
kubectl apply -f k8s/bonus-app1-service.yml -f k8s/bonus-app2-deployment.yml -f k8s/bonus-app2-service.yml
```

Output:
```text
service/app1-service created
deployment.apps/devops-info-service-app2 created
service/app2-service created
```

Generate TLS secret:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout bonus-tls.key -out bonus-tls.crt \
       -subj "/CN=local.example.com/O=local.example.com"

kubectl create secret tls bonus-local-tls \
       --key bonus-tls.key \
       --cert bonus-tls.crt \
       --dry-run=client -o yaml | kubectl apply -f -
```

Output:
```text
secret/bonus-local-tls created
```

Ingress apply + status:

```bash
kubectl apply -f k8s/bonus-ingress.yml
kubectl get ingress bonus-apps-ingress -o wide
```

Output:
```text
ingress.networking.k8s.io/bonus-apps-ingress created
NAME                 CLASS   HOSTS               ADDRESS     PORTS
bonus-apps-ingress   nginx   local.example.com   localhost   80, 443
```

Ingress description:

```bash
kubectl describe ingress bonus-apps-ingress
```

Output (excerpt):
```text
TLS:
       bonus-local-tls terminates local.example.com
Rules:
       local.example.com
       /app1(/|$)(.*) -> app1-service:80
       /app2(/|$)(.*) -> app2-service:80
```

HTTPS routing checks:

```bash
kubectl -n ingress-nginx port-forward service/ingress-nginx-controller 8081:80 8443:443
curl -ksS -H 'Host: local.example.com' https://127.0.0.1:8443/app1/health
curl -ksS -H 'Host: local.example.com' https://127.0.0.1:8443/app2/health
```

Output:
```json
{"status":"healthy","timestamp":"2026-03-26T18:14:28.723723Z","uptime_seconds":1086}
{"status":"healthy","timestamp":"2026-03-26T18:14:28.756080Z","uptime_seconds":174}
```

Resource summary across namespaces:

```bash
kubectl get ingress,svc,deploy -A
```

Output (excerpt):
```text
default       ingress.networking.k8s.io/bonus-apps-ingress   nginx   local.example.com   localhost   80,443
default       service/app1-service                            ClusterIP
default       service/app2-service                            ClusterIP
default       deployment.apps/devops-info-service-app2        2/2
ingress-nginx deployment.apps/ingress-nginx-controller        1/1
```

### Why Ingress is better than NodePort for this case

- Single entrypoint for multiple services by path (`/app1`, `/app2`).
- Native TLS termination at ingress layer.
- Cleaner routing rules compared to exposing many NodePorts.
- Closer to production traffic management model.

### Bonus Command Summary

```bash
# Install ingress controller for kind
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl -n ingress-nginx rollout status deployment/ingress-nginx-controller

# Deploy second app and internal services
kubectl apply -f k8s/bonus-app1-service.yml
kubectl apply -f k8s/bonus-app2-deployment.yml
kubectl apply -f k8s/bonus-app2-service.yml

# Create TLS secret
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout bonus-tls.key -out bonus-tls.crt -subj '/CN=local.example.com/O=local.example.com'
kubectl create secret tls bonus-local-tls --key bonus-tls.key --cert bonus-tls.crt --dry-run=client -o yaml | kubectl apply -f -

# Apply ingress
kubectl apply -f k8s/bonus-ingress.yml
kubectl get ingress bonus-apps-ingress -o wide

# Test paths and TLS
kubectl -n ingress-nginx port-forward service/ingress-nginx-controller 8081:80 8443:443
curl -ksS -H 'Host: local.example.com' https://127.0.0.1:8443/app1/health
curl -ksS -H 'Host: local.example.com' https://127.0.0.1:8443/app2/health
```