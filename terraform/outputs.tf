output "ec2_public_ip" {
  description = "Public IP of the EC2 instance."
  value       = aws_instance.fastapi.public_ip
}

output "docdb_endpoint" {
  description = "DocumentDB cluster endpoint."
  value       = aws_docdb_cluster.docdb.endpoint
}
