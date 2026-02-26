# Ansible Lab 5 - Quick Reference Guide

## Initial Setup

### 1. Prerequisites
- Ansible installed on local machine
- VM from Lab 4 running and accessible via SSH
- Docker Hub account and access token
- SSH key for VM access

### 2. First-Time Setup
```bash
cd ansible/

# Run the setup helper script
./setup.sh

# OR do it manually:

# 1. Edit inventory
vim inventory/hosts.ini
# Add your VM details: IP, username, SSH key

# 2. Install required collections
ansible-galaxy collection install community.docker
ansible-galaxy collection install community.general

# 3. Test connectivity
ansible all -m ping

# 4. Create vault for credentials
ansible-vault create group_vars/all.yml
# Add your Docker Hub credentials (see group_vars/all.yml.example)
```

## Daily Commands

### Connectivity & Info
```bash
# Ping all hosts
ansible all -m ping

# Check host details
ansible all -m setup

# Run ad-hoc command
ansible webservers -a "uptime"
ansible webservers -a "docker ps"

# View inventory
ansible-inventory --list
ansible-inventory --graph
```

### Playbook Execution

```bash
# System provisioning only
ansible-playbook playbooks/provision.yml

# Application deployment only
ansible-playbook playbooks/deploy.yml

# Full site deployment (provision + deploy)
ansible-playbook playbooks/site.yml

# With vault password prompt
ansible-playbook playbooks/deploy.yml --ask-vault-pass

# Check mode (dry run)
ansible-playbook playbooks/provision.yml --check

# With specific tags
ansible-playbook playbooks/provision.yml --tags "docker"
ansible-playbook playbooks/site.yml --skip-tags "deploy"
```

### Vault Management

```bash
# Create encrypted file
ansible-vault create group_vars/all.yml

# Edit encrypted file
ansible-vault edit group_vars/all.yml

# View encrypted file
ansible-vault view group_vars/all.yml

# Change vault password
ansible-vault rekey group_vars/all.yml

# Encrypt existing file
ansible-vault encrypt somefile.yml

# Decrypt file (careful!)
ansible-vault decrypt somefile.yml
```

### Debugging

```bash
# Verbose output (add more v's for more detail)
ansible-playbook playbooks/provision.yml -v
ansible-playbook playbooks/provision.yml -vv
ansible-playbook playbooks/provision.yml -vvv

# Show all variables for host
ansible webservers -m debug -a "var=hostvars[inventory_hostname]"

# Syntax check
ansible-playbook playbooks/provision.yml --syntax-check

# List tasks
ansible-playbook playbooks/provision.yml --list-tasks

# List hosts
ansible-playbook playbooks/provision.yml --list-hosts
```

## Common Issues & Solutions

### Issue: Module not found (e.g., docker_login)
**Solution:**
```bash
# Install the required collection
ansible-galaxy collection install community.docker

# Install Python docker library on target VM
ansible webservers -b -m pip -a "name=docker state=present executable=pip3"
```

### Issue: "Permission denied" when connecting
**Solutions:**
- Check SSH key permissions: `chmod 600 ~/.ssh/your-key.pem`
- Verify ansible_ssh_private_key_file in inventory
- Test SSH manually: `ssh -i ~/.ssh/your-key.pem user@vm-ip`

### Issue: "Vault password required"
**Solutions:**
- Use `--ask-vault-pass` flag
- Create `.vault_pass` file with password (add to .gitignore!)
- Configure in ansible.cfg: `vault_password_file = .vault_pass`

### Issue: Tasks show "changed" on second run (not idempotent)
**Check:**
- Using stateful modules? (apt, service, file, etc.)
- Using `state: present` not `state: latest`?
- Using `command` module? (not idempotent by default)
- Add `changed_when: false` for info-gathering tasks

### Issue: Docker permission denied
**Solution:**
```bash
# User needs to be in docker group and re-login
ansible webservers -b -m user -a "name={{ ansible_user }} groups=docker append=yes"
# Then user needs to logout/login or restart connection
```

## Best Practices Checklist

- [ ] Never commit `.vault_pass` or unencrypted secrets
- [ ] Use `no_log: true` for tasks with sensitive data
- [ ] Test idempotency by running playbooks twice
- [ ] Use tags for selective execution
- [ ] Use `check` mode before running on production
- [ ] Keep roles focused on single responsibility
- [ ] Document variables in defaults/main.yml
- [ ] Use handlers for service restarts
- [ ] Verify with `--syntax-check` before running
- [ ] Use meaningful task names

## Project Structure Reference

```
ansible/
├── ansible.cfg              # Ansible configuration
├── inventory/
│   └── hosts.ini           # Static inventory
├── group_vars/
│   ├── all.yml             # Encrypted variables (DO NOT commit .vault_pass!)
│   └── all.yml.example     # Template for vault file
├── roles/
│   ├── common/             # System setup
│   │   ├── defaults/main.yml
│   │   └── tasks/main.yml
│   ├── docker/             # Docker installation
│   │   ├── defaults/main.yml
│   │   ├── tasks/main.yml
│   │   └── handlers/main.yml
│   └── app_deploy/         # App deployment
│       ├── defaults/main.yml
│       ├── tasks/main.yml
│       └── handlers/main.yml
├── playbooks/
│   ├── site.yml            # Full deployment
│   ├── provision.yml       # Infrastructure only
│   └── deploy.yml          # Application only
└── docs/
    └── LAB05.md            # Lab documentation
```

## Testing Workflow

1. **Syntax Check:** `ansible-playbook playbook.yml --syntax-check`
2. **Dry Run:** `ansible-playbook playbook.yml --check`
3. **First Run:** `ansible-playbook playbook.yml`
4. **Verify Idempotency:** `ansible-playbook playbook.yml` (should show no changes)
5. **Test Application:** `curl http://vm-ip:5000/health`

## Resources

- [Ansible Documentation](https://docs.ansible.com/)
- [Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [Module Index](https://docs.ansible.com/ansible/latest/collections/index_module.html)
- [Ansible Galaxy](https://galaxy.ansible.com/)

---

**Pro Tip:** Keep this file open in a split terminal while working on the lab! 🚀
