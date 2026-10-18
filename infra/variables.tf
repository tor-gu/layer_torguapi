variable "region" {
  type    = string
  default = "us-east-1"
}

variable "layer_name" {
  description = "Name of the Lambda layer; consumers refer to it as <layer arn>:<version>"
  type        = string
  default     = "layer_torguapi"
}
