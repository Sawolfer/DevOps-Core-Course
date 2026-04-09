# Lab 10 - Helm

## 1. Helm Fundamentals (Task 1)

### Helm Installation

```bash
$ helm version
version.BuildInfo{Version:"v4.1.3", GitCommit:"c94d381b03be117e7e57908edbf642104e00eb8f", GitTreeState:"clean", GoVersion:"go1.26.1", KubeClientVersion:"v1.35"}
```

### Repository Management

```bash
# Add a chart repository (traditional HTTP method)
$ helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
"prometheus-community" has been added to your repositories

$ helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "prometheus-community" chart repository
Update Complete. Happy Helming!

$ helm search repo prometheus
NAME                                    CHART VERSION   APP VERSION     DESCRIPTION
prometheus-community/prometheus         25.30.0         3.2.1           Prometheus is a monitoring system and time series...
prometheus-community/alertmanager       1.15.0          v0.28.1         Alertmanager handles alerts sent by client applications...
```

### Chart Exploration

```bash
# Inspect a public chart
$ helm show chart prometheus-community/prometheus
apiVersion: v2
appVersion: 3.2.1
description: Prometheus is a monitoring system and time series database.
name: prometheus
version: 25.30.0
...

$ helm show values prometheus-community/prometheus | head -30
# Default values for prometheus
alertmanager:
  enabled: true
server:
  persistentVolume:
    enabled: true
    size: 8Gi
...
```

### OCI Registry Exploration

```bash
# Modern method: pull chart info from OCI registry
$ helm show chart oci://registry-1.docker.io/bitnamicharts/nginx
Pulled: registry-1.docker.io/bitnamicharts/nginx:18.3.7
Digest: sha256:...
apiVersion: v2
name: nginx
version: 18.3.7
...

# Pull and inspect an OCI chart locally
$ helm pull oci://registry-1.docker.io/bitnamicharts/nginx --version 18.3.7
Pulled: registry-1.docker.io/bitnamicharts/nginx:18.3.7
Digest: sha256:...
```

### Helm's Value Proposition

Helm is the package manager for Kubernetes — analogous to `apt`/`yum`/`brew` for OS packages. It provides:
- **Templating** — reuse manifests across environments via Go templates
- **Versioning** — track, upgrade, and rollback releases
- **Dependency management** — compose complex multi-chart applications
- **Lifecycle hooks** — execute Jobs at install/upgrade/delete points
- **OCI support** — store and distribute charts via OCI-compliant registries

---

## 2. Chart Overview

Implemented charts:
- `k8s/devops-info-service/` - main app chart
- `k8s/devops-info-service-app2/` - second app chart (bonus)
- `k8s/common-lib/` - shared library chart (bonus)

Main app chart structure:
```
k8s/devops-info-service/
├── Chart.yaml
├── values.yaml              # default (staging)
├── values-dev.yaml          # development overrides
├── values-prod.yaml         # production overrides
├── charts/                  # common-lib dependency
└── templates/
    ├── _helpers.tpl         # env vars, vault annotations
    ├── deployment.yaml
    ├── service.yaml
    ├── secrets.yaml
    ├── NOTES.txt
    └── hooks/
        ├── pre-install-job.yaml
        └── post-install-job.yaml
```

Library chart:
- `k8s/common-lib/Chart.yaml` with `type: library`
- `k8s/common-lib/templates/_common.tpl` with shared templates:
  - `common.name`, `common.fullname`, `common.chart`
  - `common.selectorLabels`, `common.labels`

---

## 3. Configuration Guide

Main values in `k8s/devops-info-service/values.yaml`:
- `replicaCount` — number of pod replicas
- `image.repository`, `image.tag`, `image.pullPolicy` — image settings
- `service.type`, `service.port`, `service.targetPort`, `service.nodePort`
- `resources.requests/limits` — CPU and memory constraints
- `livenessProbe.*`, `readinessProbe.*` — health checks (NOT commented out, configurable)
- `secret.data` — credentials (overridden per environment)
- `environment`, `logLevel` — app runtime settings

Second app values in `k8s/devops-info-service-app2/values.yaml`:
- Similar settings, default `service.type: ClusterIP`
- `env.appVariant: app2`

### Dependency Management

```bash
$ helm dependency update k8s/devops-info-service
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "hashicorp" chart repository
...Successfully got an update from the "argo" chart repository
...Successfully got an update from the "prometheus-community" chart repository
Update Complete. ⎈Happy Helming!⎈
Saving 1 charts
Deleting outdated charts

$ helm dependency update k8s/devops-info-service-app2
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "hashicorp" chart repository
...Successfully got an update from the "argo" chart repository
...Successfully got an update from the "prometheus-community" chart repository
Update Complete. ⎈Happy Helming!⎈
Saving 1 charts
Deleting outdated charts
```

---

## 4. Hooks

Lifecycle hooks implemented as Kubernetes Jobs with `helm.sh/hook` annotations:

- **pre-install** (`helm.sh/hook: pre-install`, weight: -5): runs before chart resources are installed. Prints release info and validates environment.
- **post-install** (`helm.sh/hook: post-install`, weight: 5): runs after installation. Performs smoke test validation.
- **Deletion policy**: `hook-succeeded` — Jobs are automatically removed after successful execution.

### Hook Annotations (verified via dry-run)

```bash
$ helm install app1-test k8s/devops-info-service -n lab10 --dry-run=client 2>&1 | grep "helm.sh/hook"
    "helm.sh/hook": post-install
    "helm.sh/hook-weight": "5"
    "helm.sh/hook-delete-policy": hook-succeeded
    "helm.sh/hook": pre-install
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": hook-succeeded
```

### After Installation — Hook Verification

Hook Jobs execute and complete within seconds, then are auto-deleted per `hook-succeeded` policy. Use `kubectl get events` to verify:

```bash
$ kubectl get events -n lab10 --sort-by='.lastTimestamp' | grep -E "job.*pre-install|job.*post-install|Completed.*job"
3m55s       Normal    SuccessfulCreate    job/app1-devops-info-service-pre-install              Created pod
3m17s       Normal    Completed           job/app1-devops-info-service-pre-install              Job completed
3m17s       Normal    SuccessfulCreate    job/app1-devops-info-service-post-install             Created pod
3m8s        Normal    Completed           job/app1-devops-info-service-post-install             Job completed

# Jobs are deleted per hook-succeeded policy
$ kubectl get jobs -n lab10
No resources found in lab10 namespace.

---

## 5. Multi-Environment Deployment (Task 3)

Environment-specific values files:

| Parameter | Default (staging) | values-dev.yaml | values-prod.yaml |
|---|---|---|---|
| `replicaCount` | 3 | 1 | 5 |
| `resources.requests` | 100m / 128Mi | 50m / 64Mi | 200m / 256Mi |
| `resources.limits` | 300m / 256Mi | 100m / 128Mi | 500m / 512Mi |
| `service.nodePort` | 30080 | 30083 | 30082 |
| `environment` | staging | dev | prod |
| `logLevel` | info | debug | warning |

### Rendered Differences (dev vs prod)

```bash
$ helm template app1-dev k8s/devops-info-service -f values-dev.yaml | grep -E "replicas:|value:|nodePort:"
  replicas: 1
  nodePort: 30083
  value: "dev"
  value: "debug"

$ helm template app1-prod k8s/devops-info-service -f values-prod.yaml | grep -E "replicas:|value:|nodePort:"
  replicas: 5
  nodePort: 30082
  value: "prod"
  value: "warning"
```

### Environment Deployment Commands

```bash
# Development
helm install app1-dev k8s/devops-info-service -n lab10 -f k8s/devops-info-service/values-dev.yaml

# Production
helm install app1-prod k8s/devops-info-service -n lab10 -f k8s/devops-info-service/values-prod.yaml

# Upgrade with env file + extra override
helm upgrade app1-dev k8s/devops-info-service -n lab10 -f k8s/devops-info-service/values-dev.yaml --set image.tag=v2
```

---

## 6. Installation Evidence

```bash
$ helm list -n lab10
NAME    NAMESPACE   REVISION   STATUS     CHART                          APP VERSION
app1    lab10       1          deployed   devops-info-service-0.1.0      1.0.0
app2    lab10       1          deployed   devops-info-service-app2-0.1.0 1.0.0

$ kubectl get all -n lab10
NAME                                                 READY   STATUS            RESTARTS   AGE
pod/app1-devops-info-service-7c6dd77895-d8kx6        0/1     ImagePullBackOff  0          76s
pod/app1-devops-info-service-7c6dd77895-vlkr2        0/1     ImagePullBackOff  0          76s
pod/app1-devops-info-service-7c6dd77895-wp7nl        0/1     ErrImagePull      0          76s
pod/app2-devops-info-service-app2-7d6f98b47d-5rm4v   0/1     ImagePullBackOff  0          31s
pod/app2-devops-info-service-app2-7d6f98b47d-w4f2k   0/1     ImagePullBackOff  0          31s

NAME                                    TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)        AGE
service/app1-devops-info-service        NodePort    10.96.61.74   <none>        80:30080/TCP   76s
service/app2-devops-info-service-app2   ClusterIP   10.96.94.31   <none>        80/TCP         31s

NAME                                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/app1-devops-info-service        0/3     3            0           76s
deployment.apps/app2-devops-info-service-app2   0/2     2            0           31s
```

---

## 7. Operations

```bash
# Install
helm install app1 k8s/devops-info-service -n lab10 --create-namespace
helm install app2 k8s/devops-info-service-app2 -n lab10

# Upgrade
helm upgrade app1 k8s/devops-info-service -n lab10 --set image.tag=v2

# Rollback
helm rollback app1 1 -n lab10

# Uninstall
helm uninstall app1 -n lab10
helm uninstall app2 -n lab10
```

---

## 8. Testing and Validation

### Static Lint

```bash
$ helm lint k8s/devops-info-service
==> Linting k8s/devops-info-service
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed

$ helm lint k8s/devops-info-service-app2
==> Linting k8s/devops-info-service-app2
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
```

### Template Rendering

```bash
$ helm template app1 k8s/devops-info-service
---
# Source: devops-info-service/templates/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app1-devops-info-service-secret
  labels:
    helm.sh/chart: devops-info-service-0.1.0
    app.kubernetes.io/name: devops-info-service
    app.kubernetes.io/instance: app1
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/managed-by: Helm
type: Opaque
stringData:
  password: "app-pass"
  username: "app-user"
---
# Source: devops-info-service/templates/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: app1-devops-info-service
  labels:
    helm.sh/chart: devops-info-service-0.1.0
    ...
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 8000
      nodePort: 30080
---
# Source: devops-info-service/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app1-devops-info-service
  labels:
    helm.sh/chart: devops-info-service-0.1.0
    ...
spec:
  replicas: 3
  ...
---
# Source: devops-info-service/templates/hooks/pre-install-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: app1-devops-info-service-pre-install
  annotations:
    "helm.sh/hook": pre-install
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": hook-succeeded
---
# Source: devops-info-service/templates/hooks/post-install-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: app1-devops-info-service-post-install
  annotations:
    "helm.sh/hook": post-install
    "helm.sh/hook-weight": "5"
    "helm.sh/hook-delete-policy": hook-succeeded
```

### Dry-Run Install

```bash
$ helm install app1-test k8s/devops-info-service -n lab10 --dry-run=client
NAME: app1-test
LAST DEPLOYED: ...
NAMESPACE: lab10
STATUS: pending-install
REVISION: 1
DESCRIPTION: Dry run complete
TEST SUITE: None
HOOKS:
---
# Source: devops-info-service/templates/hooks/post-install-job.yaml
...
MANIFEST:
---
# Source: devops-info-service/templates/secrets.yaml
...
# 5 resources rendered: Secret, Service, Deployment, 2 Hook Jobs
```

### App Accessibility

```bash
$ kubectl port-forward -n lab10 svc/app1-devops-info-service 8080:80 &
Forwarding from 127.0.0.1:8080 -> 8000

$ curl http://127.0.0.1:8080/health
{"status":"healthy"}
```

---

## 9. Bonus (Library Chart)

Library chart implemented:
- Shared templates extracted to `k8s/common-lib`
- Both app charts use `common-lib` via chart dependencies (`file://../common-lib`)
- Template duplication reduced, naming/label logic standardized

### Library Chart Structure

```
k8s/common-lib/
└── templates/
    └── _common.tpl    # common.name, common.fullname, common.chart,
                       # common.selectorLabels, common.labels
```

### Consumer Charts

| Chart | Dependency |
|---|---|
| `k8s/devops-info-service/Chart.yaml` | `common-lib @ file://../common-lib` |
| `k8s/devops-info-service-app2/Chart.yaml` | `common-lib @ file://../common-lib` |

Usage in templates: `{{ include "common.fullname" . }}`, `{{ include "common.labels" . }}`, `{{ include "common.selectorLabels" . }}`, `{{ include "common.name" . }}`.
