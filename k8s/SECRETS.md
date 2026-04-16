# Lab 11 - Kubernetes Secrets and HashiCorp Vault

## 1. Kubernetes Secrets Fundamentals

### 1.1 Create secret with kubectl (imperative)

```bash
kubectl create secret generic app-credentials \
  --from-literal=username=devops-user \
  --from-literal=password=devops-pass
```

### 1.2 View secret YAML

```bash
kubectl get secret app-credentials -o yaml
```

Example output (sanitized):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-credentials
type: Opaque
data:
  username: ZGV2b3BzLXVzZXI=
  password: ZGV2b3BzLXBhc3M=
```

### 1.3 Decode base64 values

```bash
echo "ZGV2b3BzLXVzZXI=" | base64 -d; echo
echo "ZGV2b3BzLXBhc3M=" | base64 -d; echo
```

Expected decoded values:

```text
devops-user
devops-pass
```

### 1.4 Encoding vs encryption

- Base64 is encoding, not encryption. Anyone with access can decode it.
- Kubernetes Secrets are not encrypted at rest by default in all cluster setups.
- Production clusters should enable etcd encryption at rest and strict RBAC.

About etcd encryption:

- etcd encryption encrypts Kubernetes API resource data before writing to etcd.
- Enable it for clusters that store sensitive data in Secret resources.
- Use KMS-backed providers in cloud/production environments.

## 2. Helm Secret Integration

Implemented in chart: `k8s/devops-info-service`.

### 2.1 Chart structure

```text
k8s/devops-info-service/
  Chart.yaml
  values.yaml
  templates/
    _helpers.tpl
    deployment.yaml
    service.yaml
    secrets.yaml
```

### 2.2 Secret template

Added `templates/secrets.yaml` with:

- `apiVersion: v1`, `kind: Secret`
- Name based on release fullname with `-secret` suffix
- Labels from shared common helpers
- `stringData` populated from values placeholders

### 2.3 Values placeholders

`values.yaml` now includes placeholder secret data:

```yaml
secret:
  enabled: true
  data:
    username: change-me
    password: change-me
```

Important: do not commit real credentials. Override at deploy time:

```bash
helm upgrade --install devops-info-service ./k8s/devops-info-service \
  --set secret.data.username="$APP_USERNAME" \
  --set secret.data.password="$APP_PASSWORD"
```

### 2.4 Deployment secret consumption

`templates/deployment.yaml` now consumes all Secret keys via `envFrom.secretRef` when enabled.

### 2.5 Verification steps

Deploy:

```bash
helm upgrade --install devops-info-service ./k8s/devops-info-service
kubectl get secret
kubectl get pods
```

Check environment variables in pod (show names only):

```bash
POD=$(kubectl get pods -l app.kubernetes.io/instance=devops-info-service -o jsonpath='{.items[0].metadata.name}')
kubectl exec "$POD" -- sh -c 'env | grep -E "^(username|password|APP_ENV|LOG_LEVEL|HOST|PORT)=" | sed "s/=.*$/=<redacted>/"'
```

Confirm `kubectl describe pod` does not print Secret values:

```bash
kubectl describe pod "$POD"
```

You should see references to Secret key names, but not plaintext values.

Live evidence:

```text
$ helm status devops-info-service
NAME: devops-info-service
LAST DEPLOYED: Thu Apr  9 18:06:31 2026
NAMESPACE: default
STATUS: deployed
REVISION: 2

==> v1/Secret
devops-info-service-secret   Opaque   2

==> v1/Service
devops-info-service   NodePort   80:30080/TCP

==> v1/Deployment
devops-info-service   3/3   3   3

==> v1/Pod(related)
devops-info-service-769ff7b857-fxkfr   2/2   Running
devops-info-service-769ff7b857-mgv2q   2/2   Running
devops-info-service-769ff7b857-wlbv7   2/2   Running
```

```text
$ kubectl get pods -l app.kubernetes.io/instance=devops-info-service
NAME                                   READY   STATUS    RESTARTS   AGE
devops-info-service-769ff7b857-fxkfr   2/2     Running   0          5m1s
devops-info-service-769ff7b857-mgv2q   2/2     Running   0          5m9s
devops-info-service-769ff7b857-wlbv7   2/2     Running   0          4m52s
```

```text
$ kubectl exec "$POD" -c devops-info-service -- sh -c 'env | grep -E "^(username|password|APP_ENV|LOG_LEVEL|HOST|PORT)=" | sed "s/=.*$/=<redacted>/"'
LOG_LEVEL=<redacted>
PORT=<redacted>
username=<redacted>
password=<redacted>
HOST=<redacted>
APP_ENV=<redacted>
```

## 3. Resource Management

Resource requests and limits are configured in `values.yaml` and applied in deployment:

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 300m
    memory: 256Mi
```

Requests vs limits:

- Requests: scheduler guarantee used to place pods.
- Limits: hard cap enforced by the kubelet/runtime.

How to choose values:

- Start with observed baseline usage.
- Set requests near steady-state p50 or p75.
- Set limits with headroom for p95 bursts.
- Revisit after load tests and production telemetry.

## 4. Vault Integration

### 4.1 Install Vault (dev mode)

```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update

kubectl create namespace vault --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install vault hashicorp/vault \
  --namespace vault \
  --set server.dev.enabled=true \
  --set injector.enabled=true

kubectl get pods -n vault
```

Expected pods:

- `vault-0`
- `vault-agent-injector-*`

Live evidence:

```text
$ kubectl get pods -n vault
NAME                                   READY   STATUS    RESTARTS   AGE
vault-0                                1/1     Running   0          11m
vault-agent-injector-8c76487db-jvl8n   1/1     Running   0          11m
```

### 4.2 Configure KV v2 and write app secret

```bash
kubectl exec -it -n vault vault-0 -- sh

vault secrets enable -path=secret kv-v2
vault kv put secret/myapp/config \
  username="devops-user" \
  password="devops-pass" \
  db_url="postgres://user:pass@postgres:5432/app" \
  api_key="example-api-key"
```

### 4.3 Enable Kubernetes auth, policy, and role

Inside `vault-0` shell:

```bash
vault auth enable kubernetes

vault write auth/kubernetes/config \
  kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443"
```

Create policy file and apply:

```bash
cat >/tmp/devops-info-service-policy.hcl <<'EOF'
path "secret/data/myapp/config" {
  capabilities = ["read"]
}
EOF

vault policy write devops-info-service /tmp/devops-info-service-policy.hcl
```

Bind role to app service account and namespace:

```bash
vault write auth/kubernetes/role/devops-info-service \
  bound_service_account_names=default \
  bound_service_account_namespaces=default \
  policies=devops-info-service \
  ttl=24h
```

Live evidence (sanitized):

```text
Success! Enabled kubernetes auth method at: kubernetes/
Success! Data written to: auth/kubernetes/config
Success! Uploaded policy: devops-info-service

Key                                         Value
---                                         -----
bound_service_account_names                 [default]
bound_service_account_namespaces            [default]
policies                                    [devops-info-service]
token_ttl                                   24h
ttl                                         24h
```

### 4.4 Enable Vault agent injection in Helm release

The chart now supports Vault injector annotations through values.

Enable with overrides:

```bash
helm upgrade --install devops-info-service ./k8s/devops-info-service \
  --set vault.enabled=true \
  --set vault.role=devops-info-service \
  --set vault.secretPath=secret/data/myapp/config \
  --set vault.renderedFileName=config
```

### 4.5 Verify secret injection

```bash
POD=$(kubectl get pods -l app.kubernetes.io/instance=devops-info-service -o jsonpath='{.items[0].metadata.name}')

kubectl exec "$POD" -- ls -la /vault/secrets
kubectl exec "$POD" -- sh -c 'sed -n "1,20p" /vault/secrets/config | sed "s/=.*$/=<redacted>/"'
```

Verify Vault annotations (note escaped dots in jsonpath keys):

```bash
kubectl get pod "$POD" -o jsonpath='{.metadata.annotations.vault\.hashicorp\.com/agent-inject}{"\n"}{.metadata.annotations.vault\.hashicorp\.com/role}{"\n"}{.metadata.annotations.vault\.hashicorp\.com/agent-inject-secret-config}{"\n"}'
```

Live evidence:

```text
$ kubectl get pod "$POD" -o jsonpath='{.metadata.annotations.vault\.hashicorp\.com/agent-inject}{"\n"}{.metadata.annotations.vault\.hashicorp\.com/role}{"\n"}{.metadata.annotations.vault\.hashicorp\.com/agent-inject-secret-config}{"\n"}'
true
devops-info-service
secret/data/myapp/config
```

```text
$ kubectl exec "$POD" -c devops-info-service -- sh -c 'ls -la /vault/secrets && echo "---" && sed -n "1,20p" /vault/secrets/config | sed "s/=.*$/=<redacted>/"'
total 8
drwxrwxrwt 2 root root   60 Apr  9 15:06 .
drwxr-xr-x 3 root root 4096 Apr  9 15:06 ..
-rw-r--r-- 1  100 1000  127 Apr  9 15:06 config
---
APP_USERNAME=<redacted>
APP_PASSWORD=<redacted>
APP_DB_URL=<redacted>
APP_API_KEY=<redacted>
```

Expected:

- File exists at `/vault/secrets/config`
- Rendered format resembles `.env` style key-value entries

Sidecar injection pattern summary:

- Vault Agent runs in the pod and authenticates with pod service account.
- Agent reads secret from Vault using configured role and policy.
- Agent writes rendered file to shared in-pod volume.
- Application reads secrets from the mounted file path.

## 5. Bonus: Vault Agent Templates and DRY Helm templates

### 5.1 Template annotation implemented

`templates/_helpers.tpl` includes a reusable helper that renders:

- `vault.hashicorp.com/agent-inject-secret-<name>`
- `vault.hashicorp.com/agent-inject-template-<name>`

The template combines multiple values (`username`, `password`, `db_url`, `api_key`) into one rendered file.

### 5.2 Dynamic rotation behavior (research notes)

- Vault Agent periodically renews/refreshes leases and cached secret data.
- For KV secrets, updates are detected by template re-render checks.
- `vault.hashicorp.com/agent-inject-command-<name>` can trigger a command after file updates (for example, SIGHUP/reload script).
- Rotation is near-real-time, bounded by agent template/render intervals and cache behavior.

### 5.3 Named templates for environment variables

`templates/_helpers.tpl` also defines:

- `devops-info-service.envVars`

`templates/deployment.yaml` now uses `include` to inject shared env vars and avoid repetition.

This demonstrates DRY in Helm charts.

## 6. Security Analysis: Kubernetes Secrets vs Vault

Kubernetes Secrets:

- Good for simple cluster-local secret distribution.
- Tight integration with K8s and easy to use.
- Weaker security posture without etcd encryption and strict RBAC.
- Limited auditing and rotation workflows compared to dedicated secret managers.

Vault:

- Strong centralized secret management and access control.
- Rich audit logging, dynamic secrets, short-lived credentials, and rotation support.
- Better fit for production and multi-environment workloads.
- Higher operational complexity than native K8s Secrets.

When to use each:

- Use Kubernetes Secrets for low-complexity labs and non-critical internal setups.
- Use Vault for production workloads, regulated environments, and dynamic credentials.

Production recommendations:

- Do not store real secrets in Git or plain `values.yaml`.
- Use Vault (or cloud secret manager) as source of truth.
- Enable etcd encryption at rest.
- Enforce least-privilege RBAC.
- Rotate secrets regularly and validate application reload behavior.
- Enable audit logging and alerting for secret access anomalies.

## 7. Validation Summary

Chart validation run:

```bash
cd k8s/devops-info-service
helm lint .
helm template devops-info-service .
```

Result: lint passed and templates render successfully.

Cluster and release runtime checks:

```text
$ kubectl cluster-info
Kubernetes control plane is running at https://127.0.0.1:61363
CoreDNS is running at https://127.0.0.1:61363/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

```text
$ kubectl get nodes
NAME                  STATUS   ROLES           AGE   VERSION
lab09-control-plane   Ready    control-plane   13d   v1.35.0
```

```text
$ helm status devops-info-service
STATUS: deployed
NAMESPACE: default
REVISION: 2
Deployment/devops-info-service: 3/3 available
Pods: 3 pods, each 2/2 Running
Secret: devops-info-service-secret (Opaque, 2 keys)
Service: devops-info-service (NodePort 80:30080/TCP)
```
