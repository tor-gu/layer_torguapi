variable "region" {
  type    = string
  default = "us-east-1"
}

variable "project" {
  description = "Prefix for the role names, and the state key prefix in state_bucket"
  type        = string
}

variable "github_repo" {
  description = "owner/name of the GitHub repository whose workflows may assume the roles"
  type        = string
}

variable "state_bucket" {
  description = "Bucket holding the Terraform state of ../ (key <project>/prod.tfstate)"
  type        = string
}

variable "layer_name" {
  description = "Name of the Lambda layer that ../ publishes"
  type        = string
}
