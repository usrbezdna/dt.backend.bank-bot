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
  zone      = "ru-central1-a"
  cloud_id  = "b1g5iekm4kbh4enphdu6"
  folder_id = "b1g8vp06auhfbk8j09np"
}

# Latest Ubuntu 22.04 image
data "yandex_compute_image" "ubuntu-2204-latest" {
  family = "ubuntu-2204-lts"
}

# Using the same subnet as specified in our zone
data "yandex_vpc_subnet" "default-subnet-a" {
  name = "default-ru-central1-a"
}

# Creating public static IP for this TestVM instance
resource "yandex_vpc_address" "remote-public-addr" {
  name = "static ip for test-vm"

  external_ipv4_address {
    zone_id = "ru-central1-a"
  }
}

# Creating Test Server instance
resource "yandex_compute_instance" "test-vm-instance" {

  depends_on = [
    yandex_vpc_address.remote-public-addr
  ]

  name = "test-instance"

  # Intel Ice Lake
  platform_id = "standard-v3"

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
      size     = 25
    }
  }

  # Creating default network interface with public static IPv4 address
  network_interface {
    subnet_id      = data.yandex_vpc_subnet.default-subnet-a.subnet_id
    ipv6           = false

    nat            = true
    nat_ip_address = yandex_vpc_address.remote-public-addr.external_ipv4_address[0].address
  }

  # Using metadata for ssh connection management
  metadata = {
    user-data = "${file("cloud-init.yaml")}"
  }

  # Sets up connection that is used for remote configuration
  connection {
    type = "ssh"
    user = "bezdna-remote"
    private_key = "${file("~/.ssh/id_rsa")}"
    host = "${self.network_interface.0.nat_ip_address}"
  }

  # And this Provisioner starts instance configuration script
  provisioner "remote-exec" {
      when = create
      script = "../shell/terraform/start-testserver-config.sh"
  }
}

# Prints Public IP of created instance
output "connection_ip" {
  value = yandex_compute_instance.test-vm-instance.network_interface.0.nat_ip_address
}
