variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "ec2_key_name" {
  description = "EC2 Key Pair"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
  default     = "vpc-0a2da643a9bbb79de"
}

variable "security_group_id" {
  description = "Security group ID"
  type        = string
  default     = "sg-060b02d1c93a6febb"
}


variable "ami" {
  description = "AMI ID for the EC2 instance."
  type        = string
  default     = "ami-0c02fb55956c7d316"
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
  default     = "t3.micro"
}

variable "docdb_username" {
  description = "MongoDB username."
  type        = string
  default     = "docdbadmin"
}

variable "docdb_password" {
  description = "MongoDB password."
  type        = string
  sensitive   = true
}

variable "aws_access_key" {
  description = "AWS access key."
  type        = string
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS secret key."
  type        = string
  sensitive   = true
}
