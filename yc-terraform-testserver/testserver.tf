# This file provides the configuration for single Yandex Compute instance.
# This instance acts like a Test Server with latest code version.

terraform {
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = ">= 0.86.0"
    }
  }
  required_version = ">= 0.13"
}

# Using Yandex Terraform provider
provider "yandex" {
  zone      = var.zone
  cloud_id  = var.cloud_id
  folder_id = var.folder_id
}

terraform {
  backend "http" {
  }
}

# Latest Ubuntu 22.04 image
data "yandex_compute_image" "ubuntu-2204-latest" {
  family = "ubuntu-2204-lts"
}

# Using the same subnet as specified in our zone
data "yandex_vpc_subnet" "default-subnet-a" {
  name = var.subnet
}

# Creating public static IP for this VM instance
resource "yandex_vpc_address" "public-addr" {
  name = var.address_name

  external_ipv4_address {
    zone_id = var.zone
  }
}

# Creating VM Instance
resource "yandex_compute_instance" "vm-instance" {

  depends_on = [
    yandex_vpc_address.public-addr
  ]

  name        = var.vm_name
  platform_id = var.platform_id

  # Resources of this instance
  resources {
    core_fraction = 20
    cores         = 2
    memory        = 2
  }

  # Boot disk with Ubuntu 22.04 LTS
  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu-2204-latest.id
      size     = var.boot_disk_size
    }
  }

  # Creating default network interface with public static IPv4 address
  network_interface {
    subnet_id = data.yandex_vpc_subnet.default-subnet-a.subnet_id
    ipv6      = false

    nat            = true
    nat_ip_address = yandex_vpc_address.public-addr.external_ipv4_address[0].address
  }

  # Using metadata for ssh connection management
  metadata = {
    user-data = "${file("cloud-init.yaml")}"
  }

  # Sets up connection that is used for remote configuration
  connection {
    type        = "ssh"
    user        = "gitlab"
    private_key = file("~/gitlab_id_rsa")
    host        = self.network_interface.0.nat_ip_address
  }

  # Copies External Nginx Config
  provisioner "file" {
    when   = create
    source      = "external-nginx.conf"
    destination = "/home/gitlab/bezdna.backend23.2tapp.cc.conf"
  }

  # And this Provisioner starts instance configuration script
  provisioner "remote-exec" {
    when   = create
    script = "../shell/terraform/start-testserver-config.sh"
  }
}

# Prints Public IP of created instance
output "connection_ip" {
  value = yandex_compute_instance.vm-instance.network_interface.0.nat_ip_address
}
