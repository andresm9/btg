resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route" "internet_access" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.gw.id
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "ec2_sg" {
  name        = "btg-sg"
  description = "Allow HTTP, HTTPS, and SSH"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "docdb_sg" {
  name        = "docdb-sg"
  description = "Allow EC2 to access DocumentDB"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 27017
    to_port         = 27017
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2_sg.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_docdb_subnet_group" "docdb_subnet" {
  name       = "docdb-subnet-group"
  subnet_ids = [aws_subnet.public.id]
}

resource "aws_docdb_cluster" "docdb" {
  cluster_identifier      = "fastapi-docdb"
  engine                 = "docdb"
  master_username        = var.docdb_username
  master_password        = var.docdb_password
  vpc_security_group_ids = [aws_security_group.docdb_sg.id]
  db_subnet_group_name   = aws_docdb_subnet_group.docdb_subnet.name
  skip_final_snapshot    = true
}

resource "aws_docdb_cluster_instance" "docdb_instance" {
  count              = 1
  identifier         = "fastapi-docdb-instance-${count.index}"
  cluster_identifier = aws_docdb_cluster.docdb.id
  instance_class     = "db.t3.medium"
  engine             = "docdb"
}

resource "aws_instance" "btg_fastapi_backend" {
  ami                    = var.ami
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  key_name               = var.ec2_key_name

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y python3 git
    git clone https://github.com/andresm9/btg.git /home/ec2-user/btg
    cd /home/ec2-user/btg
    pip3 install --no-cache-dir --upgrade -r requirements.txt
    fastapi run app/main.py --proxy-headers --port 80
  EOF

  tags = {
    Name = "FastAPI-Server"
  }
}
