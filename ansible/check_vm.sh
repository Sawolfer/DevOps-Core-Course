#!/bin/bash

echo "=================================="
echo "Checking for existing VMs..."
echo "=================================="
echo ""

# Check Yandex CLI
if command -v yc &> /dev/null; then
    echo "✅ Yandex CLI found"
    echo ""
    echo "VMs in your Yandex Cloud:"
    yc compute instance list --format json | jq -r '.[] | "\(.name)\t\(.network_interfaces[0].primary_v4_address.one_to_one_nat.address)\t\(.status)"' 2>/dev/null || echo "No VMs or error accessing Yandex Cloud"
else
    echo "❌ Yandex CLI not installed"
    echo "Install: brew install yandex-cloud/tools/yc"
fi

echo ""
echo "=================================="
echo "Options:"
echo "=================================="
echo ""
echo "1. Create VM with Terraform:"
echo "   cd terraform && terraform apply"
echo ""
echo "2. Create VM with Pulumi:"
echo "   cd pulumi && pulumi up"
echo ""
echo "3. Use existing VM manually:"
echo "   Edit ansible/inventory/hosts.ini with VM IP"
echo ""
