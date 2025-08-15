terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"  # Use AWS provider version 5.x
    }
  }
}

provider "aws" {
  region = "us-east-1"  # Deploy resources in us-east-1 region
}

variable "db_username" { default = "appuser" }  # Default database username
variable "db_password" { default = "ChangeMe123!" sensitive = true }  # Sensitive database password
variable "key_name" { default = "" }  # Optional EC2 key pair name

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"  # Main VPC with 10.0.0.0/16 CIDR
  enable_dns_support   = true  # Enable DNS resolution
  enable_dns_hostnames = true  # Enable DNS hostnames
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"  # Public subnet CIDR
  map_public_ip_on_launch = true  # Auto-assign public IP to instances
}

resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.2.0/24"  # Private subnet CIDR
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id  # Attach IGW to main VPC
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id  # Public route table for VPC
}

resource "aws_route" "public_inet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"  # Default route for internet access
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id  # Associate public subnet with public route table
}

resource "aws_security_group" "ec2_sg" {
  vpc_id = aws_vpc.main.id
  ingress { from_port = 22 to_port = 22 protocol = "tcp" cidr_blocks = ["0.0.0.0/0"] }  # Allow SSH from anywhere
  ingress { from_port = 80 to_port = 80 protocol = "tcp" cidr_blocks = ["0.0.0.0/0"] }  # Allow HTTP from anywhere
  egress { from_port = 0 to_port = 0 protocol = "-1" cidr_blocks = ["0.0.0.0/0"] }  # Allow all outbound traffic
}

resource "aws_security_group" "rds_sg" {
  vpc_id = aws_vpc.main.id
  ingress { from_port = 5432 to_port = 5432 protocol = "tcp" security_groups = [aws_security_group.ec2_sg.id] }  # Allow PostgreSQL from EC2 instances
  egress { from_port = 0 to_port = 0 protocol = "-1" cidr_blocks = ["0.0.0.0/0"] }  # Allow all outbound traffic
}

data "aws_ami" "amazon_linux2" {
  owners      = ["137112412989"]  # Official Amazon Linux 2 AMI owner
  most_recent = true  # Use most recent AMI
  filter { name = "name" values = ["amzn2-ami-hvm-*-x86_64-gp2"] }  # Filter for Amazon Linux 2 HVM AMIs
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.amazon_linux2.id  # Use latest Amazon Linux 2 AMI
  instance_type = "t3.micro"  # Use t3.micro instance type
  subnet_id     = aws_subnet.public.id  # Deploy in public subnet
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]  # Attach EC2 security group
  key_name      = var.key_name  # Optional SSH key pair
  user_data     = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y postgresql  # Install PostgreSQL client
  EOF
}

resource "aws_db_subnet_group" "db" {
  name       = "db-subnet-group"
  subnet_ids = [aws_subnet.private.id]  # Use private subnet for RDS
}

resource "aws_db_instance" "db" {
  identifier              = "mydb"  # RDS instance identifier
  engine                  = "postgres"  # PostgreSQL database
  instance_class          = "db.t3.micro"  # Use t3.micro instance class
  allocated_storage       = 20  # Allocate 20GB storage
  username                = var.db_username  # Use variable for username
  password                = var.db_password  # Use variable for password
  db_subnet_group_name    = aws_db_subnet_group.db.name  # Use DB subnet group
  vpc_security_group_ids  = [aws_security_group.rds_sg.id]  # Attach RDS security group
  skip_final_snapshot     = true  # Skip final snapshot when destroying
  publicly_accessible     = false  # Make RDS private
}

output "ec2_public_ip" { value = aws_instance.app.public_ip }  # Output EC2 public IP
output "rds_endpoint"   { value = aws_db_instance.db.address }  # Output RDS endpoint