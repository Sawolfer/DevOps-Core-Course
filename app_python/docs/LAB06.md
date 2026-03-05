# Lab 6: Advanced Ansible & CI/CD - Submission

**Name:** Savva Ponomarev

---

## Task 1: Blocks & Tags

### Implementation Summary
I refactored role tasks to use blocks, rescue, always, and consistent tag strategy:

- `roles/common/tasks/main.yml`
  - `packages` block with apt update/install
  - `rescue` for apt failures using `apt-get update --fix-missing`
  - `always` writes completion log to `/tmp/common-packages-block.log`
  - `users` block for group/user management
  - `always` writes completion log to `/tmp/common-users-block.log`
  - role tag coverage: `common`, plus block tags `packages`, `users`

- `roles/docker/tasks/main.yml`
  - `docker_install` block for repo/key/package install
  - `rescue` waits 10s, retries apt update and package install
  - `always` ensures Docker service enabled/started
  - `docker_config` block for docker group and daemon status check
  - role tag coverage: `docker`, plus `docker_install`, `docker_config`

### Tag Strategy
- `common` → entire baseline role
- `packages` → package operations only
- `users` → user/group operations only
- `docker` → entire docker role
- `docker_install` → installation steps only
- `docker_config` → docker post-install configuration
- `app_deploy`, `compose` → web app deployment
- `web_app_wipe` → controlled cleanup operations

### Execution Examples
```bash
cd ansible
ansible-playbook -i inventory/hosts.ini playbooks/provision.yml --list-tags
ansible-playbook -i inventory/hosts.ini playbooks/provision.yml --tags "docker"
ansible-playbook -i inventory/hosts.ini playbooks/provision.yml --skip-tags "common"
ansible-playbook -i inventory/hosts.ini playbooks/provision.yml --tags "packages"
ansible-playbook -i inventory/hosts.ini playbooks/provision.yml --tags "docker_install" --check
```

### Research Answers
1. **What happens if rescue block also fails?**  
   The block result is failed. `always` still runs, but play execution follows normal error behavior (stop on that host unless `ignore_errors`/error strategy modifies it).

2. **Can you have nested blocks?**  
   Yes. Ansible supports nested blocks, but they should be used carefully for readability.

3. **How do tags inherit to tasks within blocks?**  
   Tags on a block are inherited by all tasks inside that block (including rescue/always tasks unless overridden).

---

## Task 2: Docker Compose

### Role Rename and Structure
I implemented deployment role as `roles/web_app` (instead of `app_deploy`) and updated all playbooks to use `web_app`.

### Docker Compose Template
File: `roles/web_app/templates/docker-compose.yml.j2`

- Jinja2-driven service naming and image/tag selection
- Port mapping with dynamic host/container ports
- Dynamic environment variables from `app_env`
- Vault-ready secret variable `app_secret_key`
- `restart: unless-stopped`
- Dedicated bridge network (`app_net`)

### Role Dependency
File: `roles/web_app/meta/main.yml`

```yaml
dependencies:
  - role: docker
```

This guarantees Docker installation before compose deployment even when only `web_app` role is called.

### Deployment Logic
File: `roles/web_app/tasks/main.yml`

- Creates compose project directory
- Renders `docker-compose.yml`
- Deploys with `community.docker.docker_compose_v2`
- Uses `pull: always`, `recreate: auto`, `remove_orphans: true`
- Includes rescue for deployment failure diagnostics
- Includes always-log to `/tmp/<app>-deploy-block.log`

### Variables
File: `group_vars/all.yml`

Includes:
- `app_name`, `docker_image`, `docker_tag`
- `app_port`, `app_internal_port`
- `compose_project_dir`, `docker_compose_version`
- `app_env` map
- `app_secret_key` placeholder for Vault encryption

### Idempotency Validation Commands
```bash
cd ansible
ansible-galaxy collection install -r requirements.yml
ansible-playbook -i inventory/hosts.ini playbooks/deploy.yml
ansible-playbook -i inventory/hosts.ini playbooks/deploy.yml
```
Second run should show mostly `ok` states (minimal/no `changed`).

### Research Answers
1. **`restart: always` vs `unless-stopped`**  
   `always` restarts container regardless of previous manual stop (including daemon restart); `unless-stopped` restarts except when it was explicitly stopped by operator.

2. **Compose networks vs default bridge**  
   Compose creates project-scoped managed networks with service DNS and isolation by project name. Default bridge is a generic daemon-level network without compose project semantics.

3. **Can Ansible Vault variables be used in templates?**  
   Yes. Vault-decrypted variables are available like any other variable during template rendering.

---

## Task 3: Wipe Logic

### Implementation
Files:
- `roles/web_app/tasks/wipe.yml`
- `roles/web_app/tasks/main.yml`
- `roles/web_app/defaults/main.yml`

Key behavior:
- Wipe tasks are included first in `main.yml`
- Wipe executes only when `web_app_wipe | bool` is true
- Wipe tasks are tag-gated with `web_app_wipe`
- Default is safe: `web_app_wipe: false`

### Wipe Operations
- Compose stack down (`state: absent`, remove orphans)
- Remove `docker-compose.yml`
- Remove app directory
- Emit completion message

### Test Scenarios
```bash
# 1) Normal deployment (wipe should not run)
ansible-playbook -i inventory/hosts.ini playbooks/deploy.yml

# 2) Wipe only
ansible-playbook -i inventory/hosts.ini playbooks/deploy.yml -e "web_app_wipe=true" --tags web_app_wipe

# 3) Clean reinstall (wipe -> deploy)
ansible-playbook -i inventory/hosts.ini playbooks/deploy.yml -e "web_app_wipe=true"

# 4a) Safety check: tag only, variable false (wipe blocked)
ansible-playbook -i inventory/hosts.ini playbooks/deploy.yml --tags web_app_wipe
```

### Research Answers
1. **Why variable + tag together?**  
   Double safety prevents accidental destructive execution from either a mistyped variable or broad tag run.

2. **Difference from `never` tag?**  
   `never` blocks execution unless explicitly requested by tag but does not encode runtime intent. Variable + explicit tag enforces both operator intent and contextual condition.

3. **Why wipe before deploy in `main.yml`?**  
   Supports deterministic clean reinstall flow in one run: old state removed first, then fresh deployment.

4. **When clean reinstall vs rolling update?**  
   Clean reinstall is preferred for corrupted state/config drift/incompatible changes; rolling update is preferred for low downtime and incremental changes.

5. **How to extend to images/volumes wipe?**  
   Add optional gated tasks using `community.docker.docker_image` and volume removal actions, ideally with a second stronger flag (e.g., `web_app_wipe_data=true`).

---

## Task 4: CI/CD

### Implemented Workflows
- `.github/workflows/ansible-deploy.yml` (Python app)
- `.github/workflows/ansible-deploy-bonus.yml` (Bonus app)

### Workflow Features
- Trigger by path filters (Ansible-related files only)
- `ansible-lint` job before deployment
- Installs `community.docker` collection from `ansible/requirements.yml`
- Deploys with vault password from GitHub Secrets
- Builds runtime inventory from `VM_HOST` / `VM_USER`
- SSH setup from `SSH_PRIVATE_KEY`
- Verification via HTTP checks (`/` and `/health`)

### Required Secrets
- `ANSIBLE_VAULT_PASSWORD`
- `SSH_PRIVATE_KEY`
- `VM_HOST`
- `VM_USER`

### Status Badges
Added to root `README.md`:
- Python app Ansible deployment badge
- Bonus app Ansible deployment badge

> Replace `your-username` in badge URLs with your GitHub username.

### Research Answers
1. **Security implications of SSH keys in GitHub Secrets**  
   Secrets are encrypted at rest but still exposed to workflows at runtime; risk includes malicious workflow changes or compromised runners. Mitigate with environment protection rules, limited key scope, and key rotation.

2. **How to do staging → production pipeline?**  
   Use separate environments/jobs with required approvals, deploy to staging first, run smoke/integration checks, then promote same artifact/config revision to production.

3. **What to add for rollbacks?**  
   Version pinning (`docker_tag` per release), deployment metadata, health-check gates, and rollback job that redeploys previous known-good tag.

4. **Why self-hosted runner can improve security?**  
   Tighter network boundaries and data locality (no external SSH from cloud runner), but only if runner host is hardened and access-controlled.

---

## Task 5: Documentation

This file serves as complete Lab 6 documentation and includes:
- Architecture and implementation details
- Commands for all required scenarios
- Research question answers
- Bonus architecture and workflow strategy

### Evidence Collection Checklist (attach from your environment)
- [ ] `--list-tags` output screenshot
- [ ] Rescue block run screenshot/log
- [ ] Compose deployment success output
- [ ] Idempotent second-run output
- [ ] Wipe scenarios 1–4 outputs
- [ ] GitHub Actions successful runs
- [ ] `ansible-lint` success logs
- [ ] App accessibility curls (`:8000`, `:8001`)

---

## Bonus Part 1: Multi-App

### Implemented Files
- `vars/app_python.yml`
- `vars/app_bonus.yml`
- `playbooks/deploy_python.yml`
- `playbooks/deploy_bonus.yml`
- `playbooks/deploy_all.yml`

### Design
Single reusable `web_app` role deploys both apps using app-specific variables:
- Python app on port `8000`
- Bonus app on port `8001`

Wipe remains app-scoped because each app uses unique `app_name` and `compose_project_dir`.

### Bonus Test Commands
```bash
cd ansible
ansible-playbook -i inventory/hosts.ini playbooks/deploy_all.yml
ansible-playbook -i inventory/hosts.ini playbooks/deploy_python.yml -e "web_app_wipe=true" --tags web_app_wipe
ansible-playbook -i inventory/hosts.ini playbooks/deploy_bonus.yml -e "web_app_wipe=true" --tags web_app_wipe
```

---

## Bonus Part 2: Multi-App CI/CD

### Implemented Strategy: Separate Workflows
- `ansible-deploy.yml` handles Python deployment paths
- `ansible-deploy-bonus.yml` handles bonus app paths
- Shared role changes can trigger both workflows

### Why this strategy
- Better isolation and observability per app
- Independent deployment verification and failure domains
- Easier per-app policy and rollout control

---

**Key learnings:** idempotent infrastructure patterns, safe destructive-operation gating, role reusability for multi-app deployment, and pragmatic CI/CD path-filter optimization.
