terraform {
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = ">= 0.86.0"
    }
  }
  required_version = ">= 0.13"
}

locals {
  folder_id = "b1g8vp06auhfbk8j09np"
  cloud_id  = "b1g5iekm4kbh4enphdu6"
}


provider "yandex" {
  zone      = "ru-central1-a"
  cloud_id  = local.cloud_id
  folder_id = local.cloud_id
}


# Creates SA that will be used for interactions with s3
resource "yandex_iam_service_account" "service_account_for_s3" {
  folder_id = local.folder_id
  name      = "tf-test-service-account"
}

# Grants editor role to this SA (performing any operation related to resource management) 
resource "yandex_resourcemanager_folder_iam_member" "s3-sa-editor" {
  folder_id = local.folder_id
  role      = "storage.editor"
  member    = "serviceAccount:${yandex_iam_service_account.service_account_for_s3.id}"
}

# Creates static access key for SA
resource "yandex_iam_service_account_static_access_key" "s3-sa-static-key" {
  service_account_id = yandex_iam_service_account.service_account_for_s3.id
  description        = "Access key for s3 service account"
}

# And finally, this section creates the bucket 
resource "yandex_storage_bucket" "s3_bucket" {

  access_key = yandex_iam_service_account_static_access_key.s3-sa-static-key.access_key
  secret_key = yandex_iam_service_account_static_access_key.s3-sa-static-key.secret_key

  bucket                = "terraform-s3-bucket-for-tests"
  acl                   = "private"
  default_storage_class = "STANDARD"

  force_destroy         = true
}

output "key_id" {
  value = yandex_iam_service_account_static_access_key.s3-sa-static-key.access_key
}

# This value is sensitive, you should run `tf output secret_key` to see the actual one
output "secret_key" {
  value = yandex_iam_service_account_static_access_key.s3-sa-static-key.secret_key
  sensitive = true
}

output "bucket_name" {
  value = yandex_storage_bucket.s3_bucket.bucket
}