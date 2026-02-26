# Lab 05 - Ansible Fundamentals

**Student:** Savva Ponomarev

**Mail:** s.ponomarev@innopolis.university

**Date:** February 26, 2026  

---

## 1. Environment Overview

**Control Node:** macOS

**Ansible Version:** ansible [core 2.20.3]

**Target VM:** Yandex Cloud VM (Lab 04)

**Target VM IP:** 93.77.177.142

**SSH Command:** ssh -i ~/.ssh/lab04_key ubuntu@93.77.177.142

**Inventory File:** ansible/inventory/hosts.ini

**Connectivity Check:**

```bash
ansible all -m ping
```

**Result:** Success (pong)

---

## 2. Project Structure

```
ansible/
├── ansible.cfg
├── inventory/
│   └── hosts.ini
├── group_vars/
│   └── all.yml (encrypted with Ansible Vault)
├── roles/
│   ├── common/
│   ├── docker/
│   └── app_deploy/
├── playbooks/
│   ├── site.yml
│   ├── provision.yml
│   └── deploy.yml
└── docs/
    └── LAB05.md
```

**Why roles:** Roles separate responsibilities, make tasks reusable, and keep playbooks clean.

---

## 3. Role Details

### 3.1 common

**Purpose:** Base system setup for all servers.

**Key Tasks:**
- Update apt cache (with cache_valid_time)
- Install common packages (curl, git, vim, htop, python3-pip)
- Update pip
- Set timezone

**Key Variables:**
- common_packages
- system_timezone

---

### 3.2 docker

**Purpose:** Install and configure Docker Engine.

**Key Tasks:**
- Add Docker GPG key and repository
- Install Docker packages
- Enable Docker service
- Add user to docker group
- Install Python Docker SDK

**Handlers:**
- restart docker
- update apt cache

**Key Variables:**
- docker_user
- docker_packages
- docker_gpg_key_url
- docker_repo_url

---

### 3.3 app_deploy

**Purpose:** Deploy application container from Docker Hub.

**Key Tasks:**
- Log in to Docker Hub (with Vault credentials)
- Pull Docker image
- Stop and remove old container
- Run new container with port mapping
- Wait for port availability
- Verify health endpoint

**Handlers:**
- restart app
- verify app health

**Key Variables:**
- dockerhub_username
- dockerhub_password
- docker_image
- docker_image_tag
- app_port
- app_container_name
- app_restart_policy

---

## 4. Idempotency

**Provisioning:**
- Playbook: playbooks/provision.yml
- Expected behavior: first run changes state, second run reports ok

**Status:** Not executed yet. Will capture output after running provisioning twice.

---

## 5. Ansible Vault

**Vault File:** ansible/group_vars/all.yml

**Purpose:** Store Docker Hub credentials securely.

**Status:** Vault file to be created with ansible-vault.

---

## 6. Deployment Verification

**Deploy Playbook:** playbooks/deploy.yml

**Status:** First run failed (exit code 4). Will capture exact error and final output after retry.

---

## 7. Key Decisions

1. **Role-based structure** to separate concerns and enable reuse.
2. **Ansible Vault** for secure credential storage in version control.
3. **Handlers** for efficient service restarts only when changes occur.
4. **Idempotent modules** (apt, service, user) to ensure safe re-runs.

---

## 8. Next Steps

1. Run provisioning twice and document idempotency.
2. Create Ansible Vault with Docker Hub credentials.
3. Fix deployment error and re-run deploy playbook.
4. Capture output for documentation.
