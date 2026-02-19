output "instance_id" {
  description = "ID of the Compute Instance"
  value       = yandex_compute_instance.lab_vm.id
}

output "instance_public_ip" {
  description = "Public IP address of the Compute Instance"
  value       = yandex_compute_instance.lab_vm.network_interface[0].nat_ip_address
}

output "instance_private_ip" {
  description = "Private IP address of the Compute Instance"
  value       = yandex_compute_instance.lab_vm.network_interface[0].ip_address
}

output "security_group_id" {
  description = "ID of the security group"
  value       = yandex_vpc_security_group.lab_sg.id
}

output "network_id" {
  description = "ID of the VPC network"
  value       = yandex_vpc_network.lab_network.id
}

output "subnet_id" {
  description = "ID of the subnet"
  value       = yandex_vpc_subnet.lab_subnet.id
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/lab04_key ubuntu@${yandex_compute_instance.lab_vm.network_interface[0].nat_ip_address}"
}

output "image_id" {
  description = "Image ID used for the instance"
  value       = data.yandex_compute_image.ubuntu.id
}

output "zone" {
  description = "Availability zone of the instance"
  value       = yandex_compute_instance.lab_vm.zone
}
