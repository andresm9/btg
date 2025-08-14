data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_instance" "database_server" {
  ami                         = var.ami
  instance_type               = var.instance_type
  key_name                    = var.ec2_key_name
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [var.security_group_id]
  associate_public_ip_address = true

  user_data = <<-EOF
    #!/bin/bash
    sudo yum update -y
    amazon-linux-extras enable epel -y
    sudo yum install -y mongo-org
    sudo systemctl start mongod
    sudo systemctl enable mongod
  EOF

  tags = {
    Name = "Database-Server"
  }
}

resource "aws_instance" "app_server" {
  ami                         = var.ami
  instance_type               = var.instance_type
  key_name                    = var.ec2_key_name
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [var.security_group_id]
  associate_public_ip_address = true
  depends_on                  = [aws_instance.database_server]
  user_data = templatefile("${path.module}/user_data_app.sh", {
    mongo_uri     = aws_instance.database_server.private_ip
    mongo_db_name = "BTG_DB"
  })

  tags = {
    Name = "FastAPI-Server"
  }
}


