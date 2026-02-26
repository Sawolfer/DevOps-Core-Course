#!/usr/bin/env python3
"""
Pulumi Testing Script for Yandex Cloud Infrastructure
Tests infrastructure as code deployment
"""

import os
import sys
import json
from pathlib import Path

# Set up environment
os.environ["PULUMI_CONFIG_PASSPHRASE"] = ""  # No passphrase
key_path = Path("../terraform/key.json").resolve()
os.environ["YC_SERVICE_ACCOUNT_KEY_FILE"] = str(key_path)

print(f"✓ Using key.json from: {key_path}")
print(f"✓ Key file exists: {key_path.exists()}")

try:
    import pulumi
    from pulumi import automation as auto
    import pulumi_yandex as yandex
    
    print(f"✓ Pulumi version: {pulumi.__version__}")
    
    # Test 1: Can we import Yandex provider?
    print(f"✓ Yandex provider imported successfully")
    
    # Test 2: Can we create a stack?
    print("\n=== TEST: Creating/selecting stack ===")
    
    stack_name = "dev"
    project_name = "devops-lab04"
    
    def pulumi_program():
        """Define infrastructure"""
        # This is a minimal test - just create network
        network = yandex.vpc.Network("test-network", folder_id="b1gsfpff6nb6v1a4q5g8")
        return {
            "network_id": network.id
        }
    
    # Create stack using automation API
    try:
        stack = auto.select_stack(stack_name=stack_name, project_name=project_name)
        print(f"✓ Selected existing stack: {stack_name}")
    except:
        print(f"ℹ Creating new stack: {stack_name}")
        stack = auto.create_stack(stack_name=stack_name, project_name=project_name, program=pulumi_program)
        print(f"✓ Created stack: {stack_name}")
    
    # Test 3: Configuration
    print("\n=== TEST: Configuration ===")
    
    # Set config values
    config = stack.workspace.get_config("dev")
    print(f"✓ Got stack configuration")
    
    # Test 4: Preview (without creating resources)
    print("\n=== TEST: Preview (no actual changes) ===")
    print("Running pulumi preview...")
    
    try:
        preview_result = stack.preview()
        print(f"✓ Preview succeeded")
        print(f"  - Changed resources: {preview_result.change_summary}")
    except Exception as e:
        print(f"✗ Preview failed: {e}")
        sys.exit(1)
    
    print("\n✅ All tests passed!")
    print("\nNow you can run:")
    print("  cd pulumi/")
    print("  source venv/bin/activate")
    print("  export YC_SERVICE_ACCOUNT_KEY_FILE='../terraform/key.json'")
    print("  pulumi up")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nInstalling missing packages...")
    os.system("pip install -q pulumi pulumi-yandex")
    print("Please run this script again!")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
