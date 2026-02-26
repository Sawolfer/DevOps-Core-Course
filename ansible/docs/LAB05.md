# Lab 5 — Ansible Fundamentals

**Student Name:** [Your Name]  
**Date:** [Date]  
**Lab:** Lab 05 - Ansible Fundamentals

---

## 1. Architecture Overview

### Environment Details
- **Ansible Version:** [Output of `ansible --version`]
- **Control Node OS:** [Your local OS]
- **Target VM OS:** [Ubuntu version]
- **Target VM IP:** [VM IP Address]
- **Python Version on Target:** [Python version]

### Role Structure

The project uses a role-based architecture with three main roles:

```
ansible/
├── roles/
│   ├── common/          # System provisioning (packages, timezone)
│   ├── docker/          # Docker installation and configuration
│   └── app_deploy/      # Application deployment with Docker
├── playbooks/
│   ├── site.yml         # Full site deployment (all roles)
│   ├── provision.yml    # Infrastructure provisioning only
│   └── deploy.yml       # Application deployment only
└── inventory/
    └── hosts.ini        # Static inventory
```

### Why Roles Instead of Monolithic Playbooks?

**Advantages of Role-Based Architecture:**

1. **Reusability:** Roles can be used across multiple projects and playbooks
2. **Maintainability:** Each role has a clear, single responsibility
3. **Organization:** Standardized directory structure makes code easy to navigate
4. **Testing:** Roles can be tested independently
5. **Modularity:** Mix and match roles as needed
6. **Sharing:** Roles can be shared via Ansible Galaxy or Git repositories

**Example:** The `docker` role can be reused in any project that needs Docker, without modification.

---

## 2. Roles Documentation

### Role: common

**Purpose:**  
Provides basic system provisioning tasks that are common to all servers, such as updating package cache, installing essential tools, and configuring system settings.

**Tasks:**
- Update apt cache with validity check (3600 seconds)
- Install essential packages (python3-pip, curl, git, vim, htop, etc.)
- Upgrade pip to latest version
- Set system timezone

**Variables (defaults/main.yml):**
- `common_packages`: List of packages to install
- `system_timezone`: Timezone to set (default: "UTC")

**Handlers:**
None

**Dependencies:**
None

**Idempotency:**
- `apt` module with `state: present` only installs if not present
- `cache_valid_time: 3600` prevents unnecessary cache updates
- `timezone` module only changes if timezone differs

---

### Role: docker

**Purpose:**  
Installs and configures Docker CE on Ubuntu systems using the official Docker repository.

**Tasks:**
1. Install required dependencies (apt-transport-https, ca-certificates, etc.)
2. Create directory for Docker GPG key
3. Add Docker's official GPG key
4. Add Docker APT repository
5. Install Docker packages (docker-ce, docker-ce-cli, containerd.io, plugins)
6. Ensure Docker service is running and enabled on boot
7. Add user to docker group (allows non-root docker commands)
8. Install Python Docker libraries (for Ansible docker modules)

**Variables (defaults/main.yml):**
- `docker_user`: User to add to docker group (defaults to `ansible_user`)
- `docker_packages`: List of Docker packages to install
- `docker_gpg_key_url`: URL for Docker GPG key
- `docker_repo_url`: Docker repository URL

**Handlers (handlers/main.yml):**
- `restart docker`: Restarts Docker service when triggered
- `update apt cache`: Updates apt cache when repository is added

**Dependencies:**
None

**Idempotency:**
- Repository and GPG key addition is idempotent
- Package installation only occurs if packages not present
- Service state only changes if not running/enabled
- User group membership only adds if not already member

---

### Role: app_deploy

**Purpose:**  
Deploys a containerized application from Docker Hub using credentials stored in Ansible Vault.

**Tasks:**
1. Log in to Docker Hub using encrypted credentials
2. Pull latest Docker image
3. Stop existing container (if running)
4. Remove old container (if exists)
5. Run new container with proper configuration:
   - Port mapping (5000:5000)
   - Restart policy (unless-stopped)
   - Environment variables (if defined)
6. Wait for application port to be available
7. Verify application health endpoint responds

**Variables:**
- From `defaults/main.yml`:
  - `app_name`: Application name
  - `app_port`: Application port (default: 5000)
  - `app_container_name`: Container name
  - `app_restart_policy`: Docker restart policy
  - `health_check_path`: Health check endpoint
  - `app_environment`: Environment variables dict
  
- From `group_vars/all.yml` (encrypted):
  - `dockerhub_username`: Docker Hub username
  - `dockerhub_password`: Docker Hub access token
  - `docker_image`: Full image name
  - `docker_image_tag`: Image tag

**Handlers (handlers/main.yml):**
- `restart app`: Restarts application container
- `verify app health`: Checks health endpoint

**Dependencies:**
- Requires Docker to be installed (docker role)
- Requires Python docker library

**Idempotency:**
- Container operations are idempotent (stop/remove ignore errors if not exists)
- New container is always created with fresh image
- Health check is verification, not state-changing

---

## 3. Idempotency Demonstration

### First Run - provision.yml

**Command:**
```bash
ansible-playbook playbooks/provision.yml
```

**Output:**
```
[Paste terminal output from first run here]
[Look for "changed" status in yellow]
```

**Analysis - First Run:**
- **Changed Tasks:**
  - Package cache update: CHANGED (cache was outdated)
  - Install common packages: CHANGED (packages not present)
  - Install Docker repository: CHANGED (repository not configured)
  - Install Docker packages: CHANGED (Docker not installed)
  - Enable Docker service: CHANGED (service not enabled)
  - Add user to docker group: CHANGED (user not in group)
  
**Why Changes Occurred:**
The system was in its initial state. Ansible detected the actual state differed from desired state and made necessary changes to converge to the desired state.

---

### Second Run - provision.yml

**Command:**
```bash
ansible-playbook playbooks/provision.yml
```

**Output:**
```
[Paste terminal output from second run here]
[Look for "ok" status in green, ZERO "changed"]
```

**Analysis - Second Run:**
- **OK Tasks (No Changes):**
  - Package cache: OK (cache still valid, within 3600s)
  - Install packages: OK (all packages already installed)
  - Docker repository: OK (repository already configured)
  - Docker packages: OK (Docker already installed)
  - Docker service: OK (already running and enabled)
  - User in docker group: OK (user already member)

**Why No Changes:**
The system already matches the desired state. Ansible detected this and skipped making any changes. This demonstrates **idempotency** - the playbook can be run multiple times safely.

---

### What Makes These Roles Idempotent?

**Key Principles:**

1. **Declarative State:** Roles declare desired state, not actions
   - ✅ `state: present` (package should exist)
   - ❌ `command: apt install` (always runs)

2. **Stateful Modules:** Using built-in modules that check current state
   - `apt`, `service`, `user`, `file` modules are naturally idempotent

3. **Conditional Logic:** Only act when needed
   - `cache_valid_time`: Don't update cache if recent
   - `ignore_errors: yes`: Don't fail if container doesn't exist

4. **No Side Effects:** Operations don't create unintended changes
   - Appending to groups (`append: yes`) vs replacing

**Result:** Running the playbook multiple times is safe and produces consistent results!

---

## 4. Ansible Vault Usage

### How Credentials Are Stored

**Encrypted File:** `group_vars/all.yml`

This file contains sensitive information:
- Docker Hub username
- Docker Hub access token/password
- Application configuration variables

### Creating the Vault

**Command:**
```bash
ansible-vault create group_vars/all.yml
```

**Content (before encryption):**
```yaml
---
dockerhub_username: myusername
dockerhub_password: dckr_pat_xxxxxxxxxxxxx
docker_image: "myusername/devops-app"
docker_image_tag: latest
```

### Viewing Encrypted Content

**The encrypted file looks like this:**
```
$ANSIBLE_VAULT;1.1;AES256
66386439653738653...
[encrypted content]
```

**To view:**
```bash
ansible-vault view group_vars/all.yml
# OR
ansible-vault edit group_vars/all.yml
```

### Vault Password Management Strategy

**Current Strategy:**
- Vault password stored in `.vault_pass` file
- File is added to `.gitignore` (NEVER committed)
- File permissions set to 600 (owner read/write only)
- Referenced in `ansible.cfg` for automatic use

**Alternative Strategies:**
1. **Prompt for password:** Use `--ask-vault-pass` flag
2. **Environment variable:** Store password in `ANSIBLE_VAULT_PASSWORD`
3. **Password script:** Use executable that returns password

### Running Playbooks with Vault

**If using `.vault_pass` file (configured in ansible.cfg):**
```bash
ansible-playbook playbooks/deploy.yml
```

**If using manual password:**
```bash
ansible-playbook playbooks/deploy.yml --ask-vault-pass
```

### Why Ansible Vault is Important

**Security Benefits:**

1. **Safe Version Control:** Encrypted secrets can be committed to Git safely
2. **Collaboration:** Team members can access secrets without exposing them
3. **Compliance:** Meets security requirements for credential management
4. **Audit Trail:** Changes to secrets are tracked in Git
5. **No Plain Text:** Secrets never exist unencrypted in repository

**Without Vault:**
- ❌ Hardcoded passwords in plain text
- ❌ Credentials in git history forever
- ❌ Security breach if repository leaked
- ❌ No way to share playbooks safely

**With Vault:**
- ✅ Encrypted at rest in repository
- ✅ Only decrypted in memory during execution
- ✅ Safe to commit and share
- ✅ Vault password is the only secret to manage

---

## 5. Deployment Verification

### Running the Deployment

**Command:**
```bash
cd ansible
ansible-playbook playbooks/deploy.yml
```

**Terminal Output:**
```
[Paste full terminal output from deploy.yml run here]
[Include task names, status, and timing]
```

**Key Observations:**
- Docker login: OK (credentials accepted, no_log hides password)
- Image pull: CHANGED (new image pulled) or OK (image already latest)
- Container stop/remove: OK (cleanup successful)
- Container run: CHANGED (new container started)
- Wait for port: OK (port 5000 became available)
- Health check: OK (health endpoint returned 200)

---

### Container Status Verification

**Command:**
```bash
ansible webservers -a "docker ps"
```

**Output:**
```
[Paste docker ps output here showing running container]
CONTAINER ID   IMAGE                    COMMAND           STATUS         PORTS                    NAMES
abc123def456   username/devops-app:latest   "python app.py"   Up 2 minutes   0.0.0.0:5000->5000/tcp   devops-app
```

**Verification Points:**
- ✅ Container is running (Status: Up)
- ✅ Correct image and tag
- ✅ Port mapping configured (0.0.0.0:5000->5000/tcp)
- ✅ Container name matches configuration
- ✅ Restart policy applied (unless-stopped)

---

### Application Health Checks

**Health Endpoint Check:**
```bash
curl http://<VM-IP>:5000/health
```

**Output:**
```json
{
  "status": "healthy",
  "timestamp": "2024-XX-XX XX:XX:XX"
}
```

**Main Endpoint Check:**
```bash
curl http://<VM-IP>:5000/
```

**Output:**
```
[Paste application response here]
```

**Verification:**
- ✅ Health endpoint returns 200 OK
- ✅ Application responds correctly
- ✅ No connection errors
- ✅ Response time acceptable

---

### Handler Execution

**Handlers Triggered:**
- `verify app health`: Triggered after container starts
  - Status: OK
  - Made 1 HTTP request to verify health

**Handlers Not Triggered:**
- `restart docker`: Not triggered (Docker config unchanged)
- `restart app`: Not triggered (no configuration changes needed restart)

---

## 6. Key Decisions

### 1. Why use roles instead of plain playbooks?

Roles provide modular, reusable components with standardized structure. Each role has a single responsibility (common packages, Docker installation, app deployment) making the code easier to maintain, test, and reuse across different projects. This separation of concerns means I can use the Docker role in any project without modification.

### 2. How do roles improve reusability?

Roles are self-contained with their own defaults, tasks, and handlers. The `docker` role, for example, can be used in any project that needs Docker - just add it to the roles list. Variables in `defaults/main.yml` allow customization without changing the role code. This makes roles portable across projects and shareable via Ansible Galaxy.

### 3. What makes a task idempotent?

A task is idempotent when running it multiple times produces the same result without unwanted side effects. Ansible achieves this by using modules that check current state before acting - like `apt: state=present` which only installs if the package isn't already installed, or `service: state=started` which only starts if not running.

### 4. How do handlers improve efficiency?

Handlers only execute when triggered by a task that makes a change (notified). For example, the `restart docker` handler only runs if the Docker repository is added or packages are installed - not every time the playbook runs. This prevents unnecessary service restarts and makes playbooks more efficient on subsequent runs.

### 5. Why is Ansible Vault necessary?

Ansible Vault encrypts sensitive data (passwords, tokens, keys) so playbooks can be safely committed to version control. Without Vault, credentials would either be hardcoded (security risk) or stored externally (breaks infrastructure-as-code). Vault provides secure, auditable credential management that integrates seamlessly with Ansible's workflow.

---

## 7. Challenges and Solutions

### Challenge 1: Docker Module Installation
**Issue:** Initial deployment failed with "docker_login module not found"  
**Solution:** Added task in docker role to install `python3-docker` package, which provides the Docker SDK for Python that Ansible's docker modules require.

### Challenge 2: [Add your challenge]
**Issue:** [Description]  
**Solution:** [How you solved it]

### Challenge 3: [Add your challenge]
**Issue:** [Description]  
**Solution:** [How you solved it]

---

## Summary

Successfully implemented Ansible automation with:
- ✅ Role-based architecture for reusability
- ✅ Idempotent provisioning (demonstrated with two runs)
- ✅ Secure credential management with Ansible Vault
- ✅ Automated Docker installation
- ✅ Containerized application deployment
- ✅ Health check verification
- ✅ Proper handler usage for efficiency

The infrastructure can now be provisioned and deployed consistently with a single command, and the playbooks can be safely run multiple times without causing issues.

---

## Appendix A: Commands Reference

```bash
# Test connectivity
ansible all -m ping

# Run provisioning (first and second time for idempotency)
ansible-playbook playbooks/provision.yml

# Deploy application
ansible-playbook playbooks/deploy.yml

# Run full site deployment
ansible-playbook playbooks/site.yml

# View vault contents
ansible-vault view group_vars/all.yml

# Edit vault contents
ansible-vault edit group_vars/all.yml

# Check inventory
ansible-inventory --list
ansible-inventory --graph

# Ad-hoc commands
ansible webservers -a "docker ps"
ansible webservers -a "systemctl status docker"
```

---

**Lab Completion Date:** [Date]  
**Status:** ✅ Complete
