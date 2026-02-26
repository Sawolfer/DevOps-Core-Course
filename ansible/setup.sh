#!/bin/bash

# Ansible Lab 5 Setup Script
# This script helps you set up your Ansible environment

set -e

echo "=========================================="
echo "Ansible Lab 5 Setup Helper"
echo "=========================================="
echo ""

# Check if Ansible is installed
echo "Checking Ansible installation..."
if ! command -v ansible &> /dev/null; then
    echo "❌ Ansible is not installed!"
    echo ""
    echo "Please install Ansible first:"
    echo "  macOS:         brew install ansible"
    echo "  Ubuntu/Debian: sudo apt install ansible"
    echo "  Or visit: https://docs.ansible.com/ansible/latest/installation_guide/index.html"
    exit 1
fi

ANSIBLE_VERSION=$(ansible --version | head -n 1)
echo "✅ Ansible found: $ANSIBLE_VERSION"
echo ""

# Check if we're in the ansible directory
if [ ! -f "ansible.cfg" ]; then
    echo "❌ Please run this script from the ansible/ directory"
    exit 1
fi

echo "=========================================="
echo "Step 1: Configure Inventory"
echo "=========================================="
echo ""
echo "Edit inventory/hosts.ini with your VM details:"
echo "  - Replace <VM-IP-ADDRESS> with your VM's IP"
echo "  - Replace <username> with your SSH username"
echo "  - Add ansible_ssh_private_key_file if needed"
echo ""
read -p "Press Enter when you've updated inventory/hosts.ini..."
echo ""

echo "=========================================="
echo "Step 2: Test Connectivity"
echo "=========================================="
echo ""
echo "Testing connection to your VM..."
if ansible all -m ping; then
    echo "✅ Successfully connected to VM!"
else
    echo "❌ Connection failed. Please check:"
    echo "  - VM IP address in inventory/hosts.ini"
    echo "  - SSH key is correct and has proper permissions (chmod 600)"
    echo "  - VM is running and accessible"
    echo "  - Firewall allows SSH (port 22)"
    exit 1
fi
echo ""

echo "=========================================="
echo "Step 3: Install Required Collections"
echo "=========================================="
echo ""
echo "Installing Ansible collections for Docker..."
ansible-galaxy collection install community.docker
ansible-galaxy collection install community.general
echo "✅ Collections installed"
echo ""

echo "=========================================="
echo "Step 4: Create Ansible Vault"
echo "=========================================="
echo ""
echo "You need to create an encrypted vault file for Docker Hub credentials."
echo ""
read -p "Do you want to create the vault now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "You'll be prompted to:"
    echo "  1. Enter a vault password (remember this!)"
    echo "  2. Add your Docker Hub credentials in YAML format"
    echo ""
    echo "Example content to add:"
    echo "---"
    echo "dockerhub_username: your-username"
    echo "dockerhub_password: your-access-token"
    echo "docker_image: \"your-username/devops-app\""
    echo "docker_image_tag: latest"
    echo ""
    read -p "Press Enter to create vault (vim will open)..."
    
    ansible-vault create group_vars/all.yml
    
    echo ""
    echo "✅ Vault created!"
    echo ""
    echo "To edit later: ansible-vault edit group_vars/all.yml"
    echo "To view: ansible-vault view group_vars/all.yml"
else
    echo "⚠️  Skipping vault creation. You'll need to create it before deploying:"
    echo "   ansible-vault create group_vars/all.yml"
fi
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Run system provisioning:"
echo "   ansible-playbook playbooks/provision.yml"
echo ""
echo "2. Run it again to verify idempotency (should show no changes):"
echo "   ansible-playbook playbooks/provision.yml"
echo ""
echo "3. Deploy your application:"
echo "   ansible-playbook playbooks/deploy.yml"
echo ""
echo "4. Or run everything at once:"
echo "   ansible-playbook playbooks/site.yml"
echo ""
echo "📚 Documentation: docs/LAB05.md"
echo ""
echo "Good luck! 🚀"
