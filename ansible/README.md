# Ansible Configuration for Lab 5

This directory contains Ansible roles and playbooks for automated infrastructure provisioning and application deployment.

## Structure

```
ansible/
├── inventory/          # Host inventory files
├── roles/              # Reusable Ansible roles
│   ├── common/         # Common system setup
│   ├── docker/         # Docker installation
│   └── app_deploy/     # Application deployment
├── playbooks/          # Ansible playbooks
├── group_vars/         # Encrypted variables (Vault)
├── docs/               # Documentation
└── ansible.cfg         # Ansible configuration
```

## Quick Start

1. **Configure Inventory:**
   Edit `inventory/hosts.ini` with your VM details

2. **Test Connectivity:**
   ```bash
   ansible all -m ping
   ```

3. **Provision Infrastructure:**
   ```bash
   ansible-playbook playbooks/provision.yml
   ```

4. **Deploy Application:**
   ```bash
   ansible-playbook playbooks/deploy.yml --ask-vault-pass
   ```

## Documentation

See `docs/LAB05.md` for detailed documentation.
