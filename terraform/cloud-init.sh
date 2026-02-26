#!/bin/bash
# Cloud-init script for Yandex Cloud Ubuntu instance
# Sets up SSH access with provided public key

set -e

# Update system packages
apt-get update
apt-get upgrade -y

# Ensure SSH directory exists
mkdir -p /home/ubuntu/.ssh

# Add SSH public key
echo "${public_key}" >> /home/ubuntu/.ssh/authorized_keys

# Set proper permissions
chmod 700 /home/ubuntu/.ssh
chmod 600 /home/ubuntu/.ssh/authorized_keys
chown -R ubuntu:ubuntu /home/ubuntu/.ssh

# Enable SSH
systemctl enable ssh
systemctl start ssh

echo "Cloud-init setup completed"
