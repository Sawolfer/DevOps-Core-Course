# Ansible Automation (Labs 5-6)

This directory contains Ansible automation for provisioning and application deployment.

## Structure

- `inventory/` - inventory definitions
- `group_vars/` - shared variables
- `vars/` - app-specific variable sets (multi-app deployment)
- `roles/` - reusable roles (`common`, `docker`, `web_app`)
- `playbooks/` - entrypoint playbooks
- `docs/` - lab documentation and evidence

## Quick Usage

```bash
cd ansible
ansible-playbook -i inventory/hosts.ini playbooks/provision.yml
ansible-playbook -i inventory/hosts.ini playbooks/deploy.yml
```
