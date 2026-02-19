# Terraform Configuration for Yandex Cloud - Lab 04

This directory contains Terraform configuration for provisioning cloud infrastructure on Yandex Cloud as part of Lab 04.

## Prerequisites

### 1. Terraform Installation
Install Terraform 1.0 or later:
- Download: https://www.terraform.io/downloads
- Verify: `terraform version`

### 2. Yandex Cloud Account
- Sign up: https://cloud.yandex.com/
- Free tier: 1 VM, 10 GB disk, no credit card needed initially
- Works in Russia without VPN

### 3. Yandex Cloud CLI (optional but recommended)
```bash
# macOS
brew tap yandex-cloud/tap
brew install yandex-cloud-cli

# Or download from: https://cloud.yandex.com/docs/cli/quickstart
```

### 4. Service Account and Key
```bash
# Create service account via Yandex Cloud Console:
# 1. Go to https://console.cloud.yandex.ru/
# 2. Select your folder
# 3. Go to "Service accounts" → "Create account"
# 4. Give it name: "terraform"
# 5. Assign role: "editor"
# 6. Create API key and download JSON file

# Or use Yandex CLI:
yc iam service-accounts create terraform --folder-id <YOUR-FOLDER-ID>
yc iam service-accounts keys create key.json --service-account-name terraform
```

### 5. SSH Key Pair
```bash
# Generate SSH key pair locally:
ssh-keygen -t rsa -b 4096 -f ~/.ssh/lab04_key -N ""

# Verify:
ls -la ~/.ssh/lab04_key*
```

## File Structure

```
terraform/
├── .gitignore                # Excludes state files and credentials
├── .tflint.hcl              # Linting configuration
├── main.tf                  # Yandex Cloud resources
├── variables.tf             # Input variables
├── outputs.tf              # Output values
├── cloud-init.sh           # User data script for VM setup
├── terraform.tfvars.example # Configuration template
└── README.md               # This file
```

## Configuration

### 1. Get Your Folder ID and Service Account Key

```bash
# Get your Folder ID:
yc config get folder-id
# Output: b1gg86q2uctbr0as5gzg

# Create service account (if not done):
yc iam service-accounts create terraform --folder-id <YOUR-FOLDER-ID>

# Create and download key:
yc iam service-accounts keys create key.json --service-account-id <SERVICE-ACCOUNT-ID>

# Save key.json to terraform/ directory
cp ~/Downloads/key.json terraform/key.json
```

### 2. Create terraform.tfvars
```bash
cd terraform/
cp terraform.tfvars.example terraform.tfvars
```

### 3. Edit terraform.tfvars
```hcl
yandex_folder_id  = "b1gg86q2uctbr0as5gzg"  # Your Folder ID
yandex_key_file   = "./key.json"             # Path to service account key
yandex_zone       = "ru-central1-a"          # Region (a, b, or c)
service_account_id = ""                      # Leave empty if not needed
ssh_cidr_blocks    = ["YOUR.IP.ADDRESS/32"] # Your IP for SSH security
public_key_path    = "~/.ssh/lab04_key.pub"
```

### 4. Never Commit terraform.tfvars!
Already in `.gitignore`, but double-check:
```bash
cat .gitignore | grep tfvars
# Should contain: terraform.tfvars
```

## Usage

### Initialize Terraform
```bash
cd terraform/
terraform init
# Output: Terraform has been successfully configured!
```

### Validate Configuration
```bash
terraform validate
terraform fmt        # Format code
terraform fmt -check # Check formatting

# Output: Success! The configuration is valid.
```

### Plan Infrastructure
```bash
terraform plan
# Output:
# Plan: 7 to add, 0 to change, 0 to destroy.
#
# Resources to create:
# - yandex_vpc_network
# - yandex_vpc_subnet
# - yandex_vpc_security_group
# - yandex_compute_instance
```

### Apply Configuration
```bash
terraform apply
# Review and confirm: yes

# Output:
# Apply complete! Resources: 7 added, 0 changed, 0 destroyed.
#
# Outputs:
# instance_public_ip = "198.51.100.45"
# ssh_command = "ssh -i ~/.ssh/lab04_key ubuntu@198.51.100.45"
```

### View Outputs
```bash
# All outputs
terraform output

# Specific output
terraform output instance_public_ip

# Get SSH command directly
terraform output -raw ssh_command
```

### SSH into VM
```bash
# Method 1: Using terraform output
ssh -i ~/.ssh/lab04_key ubuntu@$(terraform output -raw instance_public_ip)

# Method 2: Using preformatted command
eval $(terraform output -raw ssh_command)

# First time connection - accept host key:
The authenticity of host '198.51.100.45' can't be established.
ECDSA key fingerprint is SHA256:...
Are you sure you want to continue connecting (yes/no)? yes

# You're in!
ubuntu@instance-20250219-123456:~$
```

### Destroy Infrastructure
```bash
terraform destroy
# Confirm: yes

# All resources deleted within 100% seconds!
```

## Yandex Cloud Resources Created

| Resource | Type | Purpose |
|----------|------|---------|
| yandex_vpc_network | Network | Virtual Private Network |
| yandex_vpc_subnet | Network | Subnet within VPC (10.0.1.0/24) |
| yandex_vpc_security_group | Security | Firewall rules |
| yandex_compute_instance | Compute | Virtual machine (free tier) |

## VM Specifications

- **Platform**: standard-v2 (Yandex's standard platform)
- **vCPU**: 2 cores
- **vCPU Fraction**: 20% (free tier eligible!)
- **Memory**: 1 GB
- **Disk**: 10 GB HDD
- **OS**: Ubuntu 22.04 LTS
- **Public IP**: NAT-enabled (automatically assigned)

## Cost Analysis

**Yandex Cloud Free Tier:**
- Compute instance: **Free** (within tier limits)
- Storage: **Free** (10 GB included)
- Network/Traffic: **Free** (within tier)

**Monthly Cost**: **$0** ✅

## Security Considerations

### SSH Access Control ⚠️

Default: `ssh_cidr_blocks = ["0.0.0.0/0"]` allows all IPs

**Recommended**: Restrict to your IP only
```bash
# Get your IP
curl https://api.ipify.org

# Update terraform.tfvars
ssh_cidr_blocks = ["203.0.113.45/32"]  # Your IP

# Reapply
terraform apply
```

### Protect Your Key Files
```bash
# Private key permissions
chmod 600 ~/.ssh/lab04_key

# Never commit:
# - key.json (service account)
# - *.pem, *.key files
# - terraform.tfvars
# All covered by .gitignore
```

## Troubleshooting

### Authentication Error
```
Error: Yandex.Cloud API request failed with code Unauthenticated
```

**Solutions**:
1. Check key.json is in correct path
2. Verify service account has permissions
3. Check folder_id is correct

```bash
# Test credentials
yc config set service-account-key key.json
yc compute instances list --folder-id <YOUR-FOLDER-ID>
```

### Instance Won't Start
```
Error: Instance is not ready
```

**Solution**: Wait 30-60 seconds after apply
- Instances take time to boot
- Cloud-init script runs automatically

```bash
# Check instance status
terraform output instance_id
# Then check in Yandex console or:
# yc compute instances get <instance-id> --folder-id <YOUR-FOLDER-ID>
```

### SSH Connection Refused
```
ssh: connect to host X.X.X.X port 22: Connection refused
```

**Solutions**:
1. Wait 60 seconds for SSH to start
2. Check public IP: `terraform output instance_public_ip`
3. Verify security group allows SSH port 22
4. Check key permissions: `chmod 600 ~/.ssh/lab04_key`

### State File Issues
```bash
# Backup state before operations
cp terraform.tfstate terraform.tfstate.backup

# Remote state (recommended for production):
# Configure in Terraform Cloud or S3
```

## Lab 05 Preparation

Your VM is ready for Lab 05 (Ansible):

✅ Get VM details for Ansible:
```bash
# Save these for Lab 05
terraform output instance_public_ip > ../lab05_vm_ip.txt
terraform output instance_private_ip >> ../lab05_vm_ip.txt
echo "Key location: ~/.ssh/lab04_key" >> ../lab05_vm_ip.txt
```

✅ Keep VM running for Ansible playbooks
✅ Or destroy and recreate using Terraform in Lab 05

## References

- [Terraform Documentation](https://www.terraform.io/docs)
- [Yandex Cloud Terraform Provider](https://registry.terraform.io/providers/yandex-cloud/yandex/latest/docs)
- [Yandex Cloud Documentation](https://cloud.yandex.ru/docs/)
- [Yandex Cloud Console](https://console.cloud.yandex.ru/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)

## Next Steps

1. ✅ Install Terraform and create Yandex account
2. ✅ Create service account and download key.json
3. ✅ Generate SSH key pair
4. ✅ Configure terraform.tfvars
5. ✅ Run `terraform init`
6. ✅ Run `terraform plan`
7. ✅ Run `terraform apply`
8. ✅ Verify SSH access
9. ✅ Document outputs for Lab 04 submission
10. ➡️ Use VM for Lab 05 (Ansible)

---

**Terraform on Yandex Cloud - Ready for Infrastructure as Code! 🚀**

