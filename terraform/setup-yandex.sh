#!/bin/bash

# Installation script for Yandex Cloud CLI on macOS
# This script installs all necessary tools for Lab 04 with Yandex Cloud

echo "🚀 Yandex Cloud Lab 04 Setup Script"
echo "===================================="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install Terraform
echo "📦 Installing Terraform..."
if ! command -v terraform &> /dev/null; then
    brew tap hashicorp/tap
    brew install hashicorp/tap/terraform
    echo "✅ Terraform installed"
else
    echo "✅ Terraform already installed: $(terraform version | head -1)"
fi

# Install Yandex Cloud CLI
echo "📦 Installing Yandex Cloud CLI..."
if ! command -v yc &> /dev/null; then
    brew tap yandex-cloud/tap
    brew install yandex-cloud-cli
    echo "✅ Yandex Cloud CLI installed"
    
    # Initialize Yandex CLI
    echo ""
    echo "⚙️  Initializing Yandex Cloud CLI..."
    yc init
else
    echo "✅ Yandex Cloud CLI already installed: $(yc --version)"
fi

# Generate SSH key if not exists
echo ""
echo "🔐 Checking SSH key..."
if [ ! -f ~/.ssh/lab04_key ]; then
    echo "Generating SSH key..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/lab04_key -N ""
    echo "✅ SSH key generated at ~/.ssh/lab04_key"
else
    echo "✅ SSH key already exists"
fi

# Set permissions on SSH key
chmod 600 ~/.ssh/lab04_key
chmod 644 ~/.ssh/lab04_key.pub

echo ""
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Get your Folder ID:"
echo "   yc config get folder-id"
echo ""
echo "2. Create service account:"
echo "   yc iam service-accounts create terraform"
echo ""
echo "3. Create and download key.json:"
echo "   yc iam service-accounts keys create key.json --service-account-name terraform"
echo ""
echo "4. Copy key.json to terraform/ directory:"
echo "   cp key.json terraform/"
echo ""
echo "5. Edit terraform.tfvars with your Folder ID"
echo ""
echo "6. Run Terraform:"
echo "   cd terraform/"
echo "   terraform init"
echo "   terraform plan"
echo "   terraform apply"
echo ""
echo "For more details, see terraform/YANDEX_QUICK_START.md"
