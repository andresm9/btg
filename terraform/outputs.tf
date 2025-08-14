output "app_server_ec2_public_ip" {
  description = "Public IP of the App EC2 instance."
  value       = aws_instance.app_server.public_ip
}

output "database_server_ec2_public_ip" {
  description = "Public IP of the Database EC2 instance."
  value       = aws_instance.database_server.public_ip
}
