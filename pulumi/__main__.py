"""
Lab 04 Infrastructure as Code - Pulumi Yandex Cloud Infrastructure
This file recreates the same infrastructure as the Terraform configuration using Pulumi.
"""

import pulumi
import pulumi_yandex as yandex
import base64

# Get stack configuration
config = pulumi.Config()

# Configuration variables for Yandex Cloud
folder_id = config.require("folder_id")
yandex_zone = config.get("yandex_zone") or "ru-central1-a"
environment = config.get("environment") or "lab"
project_name = config.get("project_name") or "devops-lab04"
subnet_cidr = config.get("subnet_cidr") or "10.0.1.0/24"
public_key_path = config.get("public_key_path") or "~/.ssh/lab04_key.pub"
ssh_cidr_blocks = config.get("ssh_cidr_blocks") or "0.0.0.0/0"

# Tags to apply to all resources
common_tags = {
    "Environment": environment,
    "Project": project_name,
    "CreatedBy": "Pulumi",
    "Lab": "Lab04",
}

# Read SSH public key
import os
expanded_key_path = os.path.expanduser(public_key_path)
with open(expanded_key_path) as f:
    public_key_content = f.read().strip()

# Create a VPC network
network = yandex.VpcNetwork(
    f"{project_name}-network",
    folder_id=folder_id,
    description="Network for Lab 04 infrastructure",
    opts=pulumi.ResourceOptions(
        depends_on=[],
        protect=False,
    )
)

# Create a subnet
subnet = yandex.VpcSubnet(
    f"{project_name}-subnet",
    folder_id=folder_id,
    network_id=network.id,
    zone=yandex_zone,
    v4_cidr_blocks=[subnet_cidr],
    description="Subnet for Lab 04 infrastructure",
)

# Create Security Group
security_group = yandex.VpcSecurityGroup(
    f"{project_name}-sg",
    folder_id=folder_id,
    network_id=network.id,
    description="Security group for Lab 04 VM - allows SSH, HTTP, and custom port 5000",
    ingress=[
        # SSH
        yandex.VpcSecurityGroupIngressArgs(
            protocol="TCP",
            description="SSH access",
            port=22,
            security_group_id="self",
        ),
        # SSH from any IP (alternative rule)
        yandex.VpcSecurityGroupIngressArgs(
            protocol="TCP",
            description="SSH from anywhere",
            port=22,
            v4_cidr_blocks=[ssh_cidr_blocks],
        ),
        # HTTP
        yandex.VpcSecurityGroupIngressArgs(
            protocol="TCP",
            description="HTTP",
            port=80,
            v4_cidr_blocks=["0.0.0.0/0"],
        ),
        # HTTPS
        yandex.VpcSecurityGroupIngressArgs(
            protocol="TCP",
            description="HTTPS",
            port=443,
            v4_cidr_blocks=["0.0.0.0/0"],
        ),
        # Custom port 5000
        yandex.VpcSecurityGroupIngressArgs(
            protocol="TCP",
            description="Custom app port",
            port=5000,
            v4_cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    egress=[
        yandex.VpcSecurityGroupEgressArgs(
            protocol="ANY",
            description="Allow all outbound traffic",
            v4_cidr_blocks=["0.0.0.0/0"],
        ),
    ],
)

# Cloud-init script for user data
cloud_init_script = f"""#!/bin/bash
apt-get update
apt-get upgrade -y
mkdir -p /home/ubuntu/.ssh
echo "{public_key_content}" >> /home/ubuntu/.ssh/authorized_keys
chmod 700 /home/ubuntu/.ssh
chmod 600 /home/ubuntu/.ssh/authorized_keys
chown -R ubuntu:ubuntu /home/ubuntu/.ssh
systemctl enable ssh
systemctl start ssh
"""

# Create compute instance
instance = yandex.ComputeInstance(
    f"{project_name}-vm",
    folder_id=folder_id,
    zone=yandex_zone,
    platform_id="standard-v2",
    description="Lab 04 VM for infrastructure as code",
    resources=yandex.ComputeInstanceResourcesArgs(
        cores=2,
        core_fraction=20,  # 20% vCPU for free tier
        memory=1,
    ),
    boot_disk=yandex.ComputeInstanceBootDiskArgs(
        initialize_params=yandex.ComputeInstanceBootDiskInitializeParamsArgs(
            image_id="fd80mj0q07fvq3r88d0v",  # Ubuntu 22.04 LTS image ID
            size=10,
            type="network-hdd",
        ),
    ),
    network_interfaces=[
        yandex.ComputeInstanceNetworkInterfaceArgs(
            subnet_id=subnet.id,
            security_group_ids=[security_group.id],
            nat=True,  # Assign public IP
        ),
    ],
    metadata={
        "user-data": base64.b64encode(cloud_init_script.encode()).decode(),
    },
    labels={
        "name": f"{project_name}-vm",
        "environment": environment,
        "created_by": "pulumi",
        "lab": "lab04",
    },
    opts=pulumi.ResourceOptions(depends_on=[subnet]),
)

# Export important values
pulumi.export("instance_id", instance.id)
pulumi.export("instance_name", instance.name)
pulumi.export(
    "instance_public_ip",
    instance.network_interfaces[0].nat_ip_address,
)
pulumi.export(
    "instance_private_ip",
    instance.network_interfaces[0].ip_address,
)
pulumi.export("security_group_id", security_group.id)
pulumi.export("network_id", network.id)
pulumi.export("subnet_id", subnet.id)
pulumi.export("zone", instance.zone)
pulumi.export(
    "ssh_command",
    pulumi.Output.concat(
        "ssh -i ~/.ssh/lab04_key ubuntu@",
        instance.network_interfaces[0].nat_ip_address,
    ),
)
pulumi.export(
    "connection_info",
    pulumi.Output.all(
        instance.network_interfaces[0].nat_ip_address,
        instance.id
    ).apply(
        lambda args: f"VM is running at {args[0]} (ID: {args[1]})"
    ),
)

