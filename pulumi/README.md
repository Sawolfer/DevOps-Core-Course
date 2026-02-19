# Pulumi Configuration - Lab 04

This directory contains Pulumi configuration for provisioning the same AWS infrastructure as the Terraform configuration, but using Python as the infrastructure language.

## Key Differences from Terraform

| Aspect | Terraform (HCL) | Pulumi (Python) |
|--------|-----------------|-----------------|
| **Language** | Declarative (HCL) | Imperative (Python) |
| **Configuration** | HCL blocks | Python functions |
| **Logic** | Limited (for_each, count) | Full Python language |
| **Type Safety** | Basic | Python typing |
| **Testing** | External tools | Native pytest |
| **State Backend** | Local or remote file | Pulumi Cloud (free tier) or self-hosted |

## Advantages of Pulumi (Python)

✅ **Familiar Language**: Use Python instead of learning HCL
✅ **Full Programming Power**: Use loops, functions, classes naturally
✅ **Better IDE Support**: Autocomplete, type checking, debugging
✅ **Reusable Components**: Create abstractions and libraries
✅ **Secrets Encrypted**: Default encryption for sensitive values
✅ **Native Testing**: Use pytest for infrastructure tests

## Prerequisites

1. **Pulumi CLI**: Install Pulumi
   - Download: https://www.pulumi.com/docs/install/
   - Verify: `pulumi version`

2. **Python 3.7+**: Ensure you have Python installed
   - Check: `python3 --version`

3. **AWS Account & Credentials**:
   - Ensure AWS CLI is configured: `aws configure`
   - Or set environment variables:
     ```bash
     export AWS_ACCESS_KEY_ID="your-key"
     export AWS_SECRET_ACCESS_KEY="your-secret"
     export AWS_REGION="us-east-1"
     ```

4. **SSH Key Pair** (same as Terraform):
   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/lab04_key -N ""
   ```

## File Structure

```
.
├── __main__.py          # Main infrastructure code (equivalent to Terraform main.tf)
├── Pulumi.yaml          # Project metadata
├── Pulumi.dev.yaml      # Development stack configuration
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore patterns
└── README.md           # This file
```

## Project Structure Explained

### __main__.py
Contains all infrastructure definitions in Python:
- **Import Pulumi modules**: `pulumi`, `pulumi_aws`
- **Get configuration**: via `pulumi.Config()`
- **Define resources**: VPC, subnet, security group, EC2 instance
- **Export outputs**: Public IP, SSH command, etc.

### Pulumi.yaml
Project metadata:
- `name`: Project name
- `runtime`: Language (python)
- `description`: Purpose
- `main`: Entry point

### Pulumi.dev.yaml
Stack-specific configuration:
- AWS region
- Resource names and settings
- Instance type
- CIDR blocks
- SSH key path

## Setup and Deployment

### 1. Create Python Virtual Environment
```bash
cd pulumi/
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Pulumi Stack
```bash
# This creates a new Pulumi stack (like terraform init)
pulumi stack init dev
# Or select existing:
pulumi stack select dev
```

### 4. Configure AWS Region (Optional)
```bash
pulumi config set aws:region us-east-1
```

### 5. Preview Infrastructure Changes
```bash
# Like terraform plan
pulumi preview
```

### 6. Deploy Infrastructure
```bash
# Like terraform apply
pulumi up
# You'll be prompted to confirm
```

### 7. View Outputs
```bash
pulumi stack output                    # All outputs
pulumi stack output instance_public_ip # Specific output
```

### 8. SSH into the VM
```bash
# Get the command from outputs
PUBLIC_IP=$(pulumi stack output instance_public_ip)
ssh -i ~/.ssh/lab04_key ubuntu@$PUBLIC_IP

# Or use the exported command
eval $(pulumi stack output ssh_command)
```

### 9. Destroy Infrastructure
```bash
# Like terraform destroy
pulumi destroy
# Or auto-approve (use with caution):
pulumi destroy --yes
```

## Configuration

### Change AWS Region
```bash
pulumi config set aws:region us-west-2
```

### Change Instance Type
```bash
pulumi config set devops-lab04:instance_type t2.small
```

### Set SSH Access CIDR Block (Recommended for Security)
```bash
# Restrict SSH to your IP only
pulumi config set devops-lab04:ssh_cidr_blocks "203.0.113.45/32"
```

### View Configuration
```bash
pulumi config
```

## Understanding the Code

### Resource Declaration (Imperative)
```python
# Pulumi uses function calls for resources
instance = aws.ec2.Instance(
    "my-instance",
    ami=ubuntu_ami.id,
    instance_type="t2.micro",
    # ... more settings
)
```

**vs Terraform (Declarative):**
```hcl
# Terraform uses blocks
resource "aws_instance" "my_instance" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"
  # ... more settings
}
```

### Resource Dependencies
Pulumi automatically detects dependencies from resource references:
```python
# Pulumi knows eip depends on instance because we reference instance.id
eip = aws.ec2.Eip(
    "my-eip",
    instance=instance.id,  # Implicit dependency
)
```

### Outputs
```python
# Export values to access after deployment
pulumi.export("public_ip", eip.public_ip)
pulumi.export("ssh_command", 
    pulumi.Output.concat("ssh -i ~/.ssh/lab04_key ubuntu@", eip.public_ip)
)
```

## Comparing Terraform and Pulumi

### Creating a Security Group Rule

**Terraform:**
```hcl
resource "aws_security_group" "web" {
  name = "web-sg"
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

**Pulumi (Python):**
```python
security_group = aws.ec2.SecurityGroup(
    "web-sg",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
)
```

### Using Loops

**Terraform:** (Using for_each)
```hcl
ingress {
  for_each = var.ports
  from_port = each.value
  # ...
}
```

**Pulumi:** (Native Python)
```python
ports = [22, 80, 443]
ingress = [
    aws.ec2.SecurityGroupIngressArgs(
        from_port=port,
        to_port=port,
        protocol="tcp",
    )
    for port in ports
]
```

## State Management

### Stack State
- Stored in Pulumi Cloud or self-hosted backend
- **Not stored locally** by default (unlike Terraform)
- Using self-managed backend: Set `PULUMI_BACKEND_URL`

### View Stack History
```bash
pulumi history
```

### Refresh Stack State
```bash
pulumi refresh
```

## Cost Management

- **t2.micro**: Free tier eligible (750 hours/month)
- **Free tier offsets**: 1 GB data transfer, VPC, Security Groups
- **Set reminders** to destroy resources if not using

## Troubleshooting

### Python Virtual Environment Not Activated
```bash
# Make sure to activate venv in each terminal session
source venv/bin/activate
```

### SSH Key Not Found
```bash
# Verify key exists
ls -la ~/.ssh/lab04_key

# Create key if missing
ssh-keygen -t rsa -b 4096 -f ~/.ssh/lab04_key -N ""
```

### Pulumi Cloud Login Required
```bash
# First time using Pulumi
pulumi login

# Then create stack
pulumi stack init dev
```

### Permission Denied with SSH
```bash
# Fix key permissions
chmod 600 ~/.ssh/lab04_key

# Verify instance is fully booted (wait a minute)
```

## Lab 05 Preparation

This VM is ready for Lab 05 (Ansible):

**To use in Lab 05:**
1. Get the public IP: `pulumi stack output instance_public_ip`
2. Document it for Lab 05
3. Keep the VM running

**Or destroy after testing:**
```bash
pulumi destroy
```

## Testing Infrastructure (Advanced)

You can write Python tests for your infrastructure:

```python
# test_infrastructure.py
import unittest
import pulumi

class TestInfrastructure(unittest.TestCase):
    def test_instance_type(self):
        # Run pulumi preview to get outputs
        # Verify instance_type matches expected value
        pass
```

Run tests:
```bash
pytest test_infrastructure.py
```

## References

- [Pulumi Documentation](https://www.pulumi.com/docs/)
- [Pulumi AWS Provider](https://www.pulumi.com/registry/packages/aws/)
- [Python Documentation](https://www.pulumi.com/docs/languages-sdks/python/)
- [Pulumi Examples](https://github.com/pulumi/examples)
- [Pulumi vs Terraform](https://www.pulumi.com/docs/concepts/vs/terraform/)
- [AWS Free Tier](https://aws.amazon.com/free/)

## Next Steps

1. ✅ Set up virtual environment
2. ✅ Install dependencies
3. ✅ Configure AWS credentials
4. ✅ Initialize stack: `pulumi stack init dev`
5. ✅ Preview: `pulumi preview`
6. ✅ Deploy: `pulumi up`
7. ✅ Verify SSH access
8. ✅ Document for Lab 04 submission
9. ➡️ Consider differences vs Terraform
10. ➡️ Keep VM for Lab 05 or destroy

---

**Pulumi: Infrastructure as Code with Modern Programming Languages** 🚀
