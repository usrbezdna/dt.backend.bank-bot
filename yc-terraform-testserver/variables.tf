

##################### Provider ##################### 

variable "cloud_id" {
  default = "b1g5iekm4kbh4enphdu6"
  type    = string
}

variable "folder_id" {
  default = "b1g8vp06auhfbk8j09np"
  type    = string
}

variable "zone" {
  default = "ru-central1-a"
  type    = string
}


##################### Network ##################### 

variable "subnet" {
  default = "default-ru-central1-a"
  type    = string
}

variable "address_name" {
  default = "static ip for test-vm"
  type    = string
}


##################### Compute Instance ##################### 

variable "vm_name" {
  default = "test-instance"
  type    = string
}

variable "platform_id" {
  default = "standard-v3"
  type    = string
}

variable "boot_disk_size" {
  default = 25
  type    = number
}