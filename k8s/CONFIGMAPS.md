# Lab 12 - ConfigMaps and Persistent Volumes

## 1. Changes in Application

### Visits counter implementation

In [app_python/app.py](../app_python/app.py):
- Added file-based visits counter.
- Added thread lock (`threading.Lock`) for safe concurrent updates.
- Counter value is read from file on startup (`0` when file does not exist).
- On each `GET /` request, the counter is incremented and atomically written back.

Atomic write flow:
1. Write value to temporary file.
2. Replace target file with `os.replace(...)`.

### New endpoint

- `GET /visits` returns current counter value:

```json
{
  "visits": 12
}
```

### Local testing with Docker

In [monitoring/docker-compose.yml](../monitoring/docker-compose.yml):
- Added `VISITS_FILE=/app/data/visits` for service `app-python`.
- Added bind mount `../app_python/data:/app/data`.

Verification commands:

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

Expected: visits value after restart is preserved.

## 2. ConfigMap Implementation

### Chart files

- [k8s/devops-info-service/files/config.json](devops-info-service/files/config.json)
- [k8s/devops-info-service/templates/configmap.yaml](devops-info-service/templates/configmap.yaml)

### File-based ConfigMap

`config.json` is loaded via `.Files.Get` into ConfigMap `devops-info-service-config`.

Template fragment:

```yaml
data:
  config.json: |-
{{ .Files.Get "files/config.json" | indent 4 }}
```

### ConfigMap as environment variables

Second ConfigMap `devops-info-service-env` provides key-value settings:
- `APP_ENV`
- `LOG_LEVEL`
- `FEATURE_VISITS_COUNTER`

Deployment uses `envFrom.configMapRef` to inject all keys.

### Mounted config file

In deployment:
- ConfigMap volume is mounted to `/config`.
- File available as `/config/config.json`.

Verification commands:

```bash
POD=$(kubectl get pods -l app.kubernetes.io/name=devops-info-service -o jsonpath='{.items[0].metadata.name}')
kubectl get configmap
kubectl exec "$POD" -- cat /config/config.json
kubectl exec "$POD" -- printenv | grep -E 'APP_ENV|LOG_LEVEL|FEATURE_VISITS_COUNTER'
```

Captured output:

```text
$ kubectl get configmap,pvc -n default
NAME                                   DATA   AGE
configmap/devops-info-service-config   1      10m
configmap/devops-info-service-env      3      10m
configmap/kube-root-ca.crt             1      20d

NAME                                             STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/devops-info-service-data   Bound    pvc-cfad4cb6-d196-4828-bd85-ca0fc34a807c   100Mi      RWO            standard       <unset>                 10m

$ POD=$(kubectl get pods -n default -l app.kubernetes.io/name=devops-info-service -o jsonpath='{.items[0].metadata.name}')
$ echo "$POD"
devops-info-service-7db47578cb-2gwr5

$ kubectl exec -n default "$POD" -- cat /config/config.json
{
  "applicationName": "devops-info-service",
  "environment": "dev",
  "settings": {
    "enableMetrics": true,
    "enableVisitsCounter": true,
    "configSource": "configmap-file"
  }
}

$ kubectl exec -n default "$POD" -- sh -lc "printenv | grep -E 'APP_ENV|LOG_LEVEL|FEATURE_VISITS_COUNTER|VISITS_FILE'"
LOG_LEVEL=info
FEATURE_VISITS_COUNTER=true
VISITS_FILE=/app/data/visits
APP_ENV=dev
```

Conclusion:
- ConfigMap file is mounted and readable at `/config/config.json`.
- Environment variables are injected from ConfigMap (`APP_ENV`, `LOG_LEVEL`, `FEATURE_VISITS_COUNTER`) plus chart env (`VISITS_FILE`).

Required env output snippet:

```text
APP_ENV=dev
LOG_LEVEL=info
FEATURE_VISITS_COUNTER=true
```

Screenshots:
- ConfigMap and PVC list: [k8s/screenshots/lab12_1.png](screenshots/lab12_1.png)
- Config file inside pod: [k8s/screenshots/lab12_2.png](screenshots/lab12_2.png)
- APP env output: [k8s/screenshots/lab12_3.png](screenshots/lab12_3.png)

## 3. Persistent Volume (PVC)

### PVC configuration

Added [k8s/devops-info-service/templates/pvc.yaml](devops-info-service/templates/pvc.yaml):
- Access mode: `ReadWriteOnce`
- Requested storage: `100Mi` by default
- Optional `storageClassName` from values

Values in [k8s/devops-info-service/values.yaml](devops-info-service/values.yaml):

```yaml
persistence:
  enabled: true
  size: 100Mi
  storageClass: ""
  mountPath: /app/data
  visitsFileName: visits
```

### Volume mount in Deployment

Deployment mounts PVC at `/app/data`. App writes counter to `/app/data/visits` through env var `VISITS_FILE`.

Verification commands:

```bash
kubectl get pvc
kubectl describe pvc devops-info-service-data
POD=$(kubectl get pods -l app.kubernetes.io/name=devops-info-service -o jsonpath='{.items[0].metadata.name}')
kubectl exec "$POD" -- cat /app/data/visits
```

Captured output:

```text
$ kubectl get pvc -n default devops-info-service-data -o wide
NAME                       STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE   VOLUMEMODE
devops-info-service-data   Bound    pvc-cfad4cb6-d196-4828-bd85-ca0fc34a807c   100Mi      RWO            standard       <unset>                 10m   Filesystem

$ POD=$(kubectl get pods -n default -l app.kubernetes.io/name=devops-info-service -o jsonpath='{.items[0].metadata.name}')
$ kubectl exec -n default "$POD" -- cat /app/data/visits
2
```

Conclusion:
- PVC is in `Bound` state with `RWO` and requested size `100Mi`.
- Visits data is stored in `/app/data/visits` on the mounted persistent volume.

### Persistence test evidence

Before deletion:

```bash
POD=$(kubectl get pods -n default -l app.kubernetes.io/name=devops-info-service -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n default "$POD" -- sh -lc "curl -s http://127.0.0.1:8000/ >/dev/null; curl -s http://127.0.0.1:8000/ >/dev/null; curl -s http://127.0.0.1:8000/visits"
```

Pod recreation:

```bash
OLD_POD=$(kubectl get pods -n default -l app.kubernetes.io/name=devops-info-service -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod -n default "$OLD_POD" --wait=true
kubectl wait -n default --for=condition=ready pod -l app.kubernetes.io/name=devops-info-service --timeout=180s
```

After new pod is ready:

```bash
NEW_POD=$(kubectl get pods -n default -l app.kubernetes.io/name=devops-info-service -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n default "$NEW_POD" -- sh -lc "curl -s http://127.0.0.1:8000/visits"
```

Captured output:

```text
$ POD=$(kubectl get pods -n default -l app.kubernetes.io/name=devops-info-service -o jsonpath='{.items[0].metadata.name}')
$ kubectl exec -n default "$POD" -- sh -lc "curl -s http://127.0.0.1:8000/ >/dev/null; curl -s http://127.0.0.1:8000/ >/dev/null; curl -s http://127.0.0.1:8000/visits"
{"visits":3}

$ OLD_POD=$(kubectl get pods -n default -l app.kubernetes.io/name=devops-info-service -o jsonpath='{.items[0].metadata.name}')
$ echo "$OLD_POD"
devops-info-service-7db47578cb-dbpw6
$ kubectl delete pod -n default "$OLD_POD" --wait=true
pod "devops-info-service-7db47578cb-dbpw6" deleted from default namespace

$ NEW_POD=$(kubectl get pods -n default -l app.kubernetes.io/name=devops-info-service -o jsonpath='{.items[0].metadata.name}')
$ echo "$NEW_POD"
devops-info-service-7db47578cb-kws6q
$ kubectl exec -n default "$NEW_POD" -- sh -lc "curl -s http://127.0.0.1:8000/visits"
{"visits":3}
```

Conclusion:
- Visits counter remained the same after pod deletion and recreation (`3` before, `3` after).
- Persistent storage works as required by Lab 12.

Screenshot:
- Persistence before/after pod deletion: [k8s/screenshots/lab12_4.png](screenshots/lab12_4.png)

## 4. ConfigMap vs Secret

Use ConfigMap when:
- Data is not sensitive.
- You store app config, feature flags, log levels, endpoints.

Use Secret when:
- Data is sensitive.
- You store passwords, API tokens, certificates, private keys.

Key differences:
- ConfigMap stores plain config values.
- Secret is intended for sensitive data and supports dedicated handling patterns (RBAC restrictions, external secret stores, etc.).
- Both can be consumed as files or environment variables.
