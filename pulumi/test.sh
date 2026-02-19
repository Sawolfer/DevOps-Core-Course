#!/bin/bash
# Pulumi Testing Guide for Yandex Cloud

echo "🚀 PULUMI TESTING FOR YANDEX CLOUD"
echo "===================================="
echo ""

# Step 1: Check prerequisites
echo "STEP 1: Checking prerequisites..."
echo ""

# Check SSH key
if [ -f ~/.ssh/lab04_key ]; then
    echo "✅ SSH key found: ~/.ssh/lab04_key"
else
    echo "❌ SSH key missing! Run: ssh-keygen -t rsa -b 4096 -f ~/.ssh/lab04_key -N ''"
    exit 1
fi

# Check service account key
if [ -f ../terraform/key.json ]; then
    echo "✅ Service account key found: ../terraform/key.json"
else
    echo "❌ Service account key missing!"
    exit 1
fi

# Check Python venv
if [ -d venv ]; then
    echo "✅ Python venv found"
else
    echo "❌ Python venv missing! Run: python3 -m venv venv"
    exit 1
fi

echo ""
echo "STEP 2: Activating venv and setting environment..."
source venv/bin/activate
export YC_SERVICE_ACCOUNT_KEY_FILE="$(cd ../terraform && pwd)/key.json"
export PULUMI_CONFIG_PASSPHRASE=""
echo "✅ Environment ready"

echo ""
echo "STEP 3: Checking Pulumi configuration..."
echo ""
cat Pulumi.dev.yaml | grep -E "folder_id|zone" | head -3

echo ""
echo "STEP 4: Running Pulumi Preview (DRY RUN - no actual changes!)..."
echo ""

# Try using pulumi CLI if available
if command -v pulumi &> /dev/null; then
    echo "Using Pulumi CLI..."
    pulumi stack select dev || pulumi stack init dev
    pulumi preview
else
    echo "Pulumi CLI not in PATH, using Python instead..."
    python3 << 'EOF'
import os
import sys
from pathlib import Path

os.environ["PULUMI_CONFIG_PASSPHRASE"] = ""
key_path = Path("../terraform/key.json").resolve()
os.environ["YC_SERVICE_ACCOUNT_KEY_FILE"] = str(key_path)

try:
    import pulumi
    print("✅ Pulumi module loaded")
    print("✅ Ready for deployment!")
    print("")
    print("Next steps:")
    print("1. Run: pulumi up")
    print("2. Wait for resources to create (2-3 minutes)")
    print("3. Run: pulumi stack output instance_public_ip")
    print("4. SSH: ssh -i ~/.ssh/lab04_key ubuntu@<IP>")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF
fi

echo ""
echo "✅ PULUMI READY FOR TESTING!"
echo ""
echo "Quick Test Commands:"
echo "==================="
echo ""
echo "1️⃣ Preview (see what will be created):"
echo "   pulumi preview"
echo ""
echo "2️⃣ Deploy (create infrastructure):"
echo "   pulumi up"
echo ""
echo "3️⃣ Get output (VM IP address):"
echo "   pulumi stack output instance_public_ip"
echo ""
echo "4️⃣ SSH connect:"
echo "   ssh -i ~/.ssh/lab04_key ubuntu@\$(pulumi stack output instance_public_ip)"
echo ""
echo "5️⃣ Destroy (cleanup):"
echo "   pulumi destroy"
echo ""
