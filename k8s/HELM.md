# Lab 10 - Helm

## 1. Chart Overview

Implemented charts:
- `k8s/devops-info-service/` - main app chart
- `k8s/devops-info-service-app2/` - second app chart (bonus)
- `k8s/common-lib/` - shared library chart (bonus)

Main app chart structure:
- `Chart.yaml` - metadata and dependency on `common-lib`
- `values.yaml` - default configuration
- `templates/deployment.yaml` - Deployment template
- `templates/service.yaml` - Service template
- `templates/NOTES.txt` - post-install usage info

Library chart:
- `k8s/common-lib/Chart.yaml` with `type: library`
- `k8s/common-lib/templates/_common.tpl` with shared templates:
  - `common.name`
  - `common.fullname`
  - `common.chart`
  - `common.selectorLabels`
  - `common.labels`

## 2. Configuration Guide

Main values in `k8s/devops-info-service/values.yaml`:
- `replicaCount` - number of pod replicas
- `image.repository`, `image.tag`, `image.pullPolicy` - image settings
- `service.type`, `service.port`, `service.targetPort`, `service.nodePort`
- `resources.requests/limits` - CPU and memory constraints
- `livenessProbe.*`, `readinessProbe.*` - health checks

Second app values in `k8s/devops-info-service-app2/values.yaml`:
- Similar settings, default `service.type: ClusterIP`
- `env.appVariant: app2`

Examples:

```bash
# Render main app with defaults
helm template app1 k8s/devops-info-service

# Install main app with custom replicas
helm install app1 k8s/devops-info-service --set replicaCount=2

# Install app2 with custom image tag
helm install app2 k8s/devops-info-service-app2 --set image.tag=v2
```

## 3. Hooks Status

Hook templates (`pre-install`, `post-install`) are not implemented yet in the current chart state.

Planned implementation files:
- `k8s/devops-info-service/templates/hooks/pre-install-job.yaml`
- `k8s/devops-info-service/templates/hooks/post-install-job.yaml`

## 4. Installation Evidence Checklist

Run and collect outputs:

```bash
helm version
helm dependency update k8s/devops-info-service
helm dependency update k8s/devops-info-service-app2
helm lint k8s/devops-info-service
helm lint k8s/devops-info-service-app2
helm template app1 k8s/devops-info-service
helm template app2 k8s/devops-info-service-app2
helm install app1 k8s/devops-info-service -n lab10 --create-namespace
helm install app2 k8s/devops-info-service-app2 -n lab10
helm list -n lab10
kubectl get all -n lab10
```

If you get API connection errors (for example `connection refused`), start or recreate your local cluster first:

```bash
kind create cluster --name lab10
kubectl cluster-info
kubectl get nodes
```

## 5. Operations

```bash
# Upgrade
helm upgrade app1 k8s/devops-info-service -n lab10 --set image.tag=v2

# Rollback
helm rollback app1 1 -n lab10

# Uninstall
helm uninstall app1 -n lab10
helm uninstall app2 -n lab10
```

## 6. Testing and Validation

```bash
# Static checks
helm lint k8s/devops-info-service
helm lint k8s/devops-info-service-app2

# Dry-run install
helm install app1 k8s/devops-info-service -n lab10 --dry-run --debug

# App accessibility
kubectl port-forward -n lab10 svc/app1-devops-info-service 8080:80
curl http://127.0.0.1:8080/health
```

## 7. Bonus (Library Chart)

Bonus implemented:
- Shared templates extracted to `k8s/common-lib`
- Both app charts use `common-lib` via chart dependencies
- Template duplication reduced and naming/label logic standardized
