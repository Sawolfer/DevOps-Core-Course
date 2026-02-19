variable "yandex_folder_id" {
  description = "Yandex Cloud Folder ID"
  type        = string
}

variable "yandex_zone" {
  description = "Yandex Cloud availability zone"
  type        = string
  default     = "ru-central1-a"
}

variable "yandex_key_file" {
  description = "Path to Yandex Cloud service account key file"
  type        = string
  default     = "./key.json"
}

variable "service_account_id" {
  description = "Service account ID for the VM (optional)"
  type        = string
  default     = ""
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "lab"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "devops-lab04"
}

variable "subnet_cidr" {
  description = "CIDR block for subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "public_key_path" {
  description = "Path to SSH public key file"
  type        = string
  default     = "~/.ssh/lab04_key.pub"
}

variable "ssh_cidr_blocks" {
  description = "CIDR blocks allowed for SSH access (set to your IP)"
  type        = list(string)
  default     = ["0.0.0.0/0"] # CHANGE THIS to your IP for security! e.g., ["1.2.3.4/32"]
}
