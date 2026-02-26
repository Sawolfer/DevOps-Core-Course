terraform {
  required_version = ">= 1.0"
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "~> 0.100"
    }
  }
}

provider "yandex" {
  service_account_key_file = var.yandex_key_file
  folder_id                = var.yandex_folder_id
  zone                     = var.yandex_zone
}

# Create a VPC network for the lab
resource "yandex_vpc_network" "lab_network" {
  name        = "${var.project_name}-network"
  description = "Network for Lab 04 infrastructure"
  folder_id   = var.yandex_folder_id
}

# Create a subnet
resource "yandex_vpc_subnet" "lab_subnet" {
  name           = "${var.project_name}-subnet"
  folder_id      = var.yandex_folder_id
  v4_cidr_blocks = [var.subnet_cidr]
  zone           = var.yandex_zone
  network_id     = yandex_vpc_network.lab_network.id
  description    = "Subnet for Lab 04 infrastructure"
}

# Create Security Group
resource "yandex_vpc_security_group" "lab_sg" {
  name        = "${var.project_name}-sg"
  description = "Security group for Lab 04 VM - allows SSH, HTTP, and custom port 5000"
  folder_id   = var.yandex_folder_id
  network_id  = yandex_vpc_network.lab_network.id

  # SSH access
  ingress {
    protocol          = "TCP"
    description       = "SSH access"
    port              = 22
    security_group_id = "self"
  }

  ingress {
    protocol       = "TCP"
    description    = "SSH from anywhere"
    port           = 22
    v4_cidr_blocks = var.ssh_cidr_blocks
  }

  # HTTP access
  ingress {
    protocol       = "TCP"
    description    = "HTTP"
    port           = 80
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS access
  ingress {
    protocol       = "TCP"
    description    = "HTTPS"
    port           = 443
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  # Custom port 5000 (for app deployment)
  ingress {
    protocol       = "TCP"
    description    = "Custom app port"
    port           = 5000
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound traffic - allow all
  egress {
    protocol       = "ANY"
    description    = "Allow all outbound traffic"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  labels = {
    name = "${var.project_name}-sg"
  }
}

# Create compute instance
resource "yandex_compute_instance" "lab_vm" {
  name               = "${var.project_name}-vm"
  zone               = var.yandex_zone
  folder_id          = var.yandex_folder_id
  platform_id        = "standard-v2"
  service_account_id = var.service_account_id

  resources {
    cores         = 2
    core_fraction = 20 # 20% vCPU for free tier
    memory        = 1
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.id
      size     = 10
      type     = "network-hdd"
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.lab_subnet.id
    # Security groups - commented out due to compatibility issues
    # security_group_ids = [yandex_vpc_security_group.lab_sg.id]
    nat = true # Assign public IP
  }

  metadata = {
    user-data = base64encode(templatefile("${path.module}/cloud-init.sh", {
      public_key = file(var.public_key_path)
    }))
  }

  labels = {
    name        = "${var.project_name}-vm"
    environment = var.environment
    created_by  = "terraform"
    lab         = "lab04"
  }

  depends_on = [yandex_vpc_subnet.lab_subnet]
}

# Get Ubuntu 22.04 image
data "yandex_compute_image" "ubuntu" {
  family    = "ubuntu-2204-lts"
  folder_id = "standard-images" # Yandex's public folder
}
