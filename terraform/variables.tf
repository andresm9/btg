variable "aws_region" {
  description = "AWS region to deploy resources."
  type        = string
  default     = "us-east-1"
}

variable "ec2_key_name" {
  description = "Name of the EC2 Key Pair to allow SSH access."
  type        = string
}

variable "ami" {
  description = "AMI ID for the EC2 instance."
  type        = string
  default     = "ami-0c02fb55956c7d316" # Amazon Linux 2 AMI (update as needed)
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
  default     = "t3.micro"
}

variable "docdb_username" {
  description = "DocumentDB master username."
  type        = string
  default     = "docdbadmin"
}

variable "docdb_password" {
  description = "DocumentDB master password."
  type        = string
  sensitive   = true
}
