############################################################
# main.tf — VPC + ALB + EC2 AutoScaling + RDS (PostgreSQL)
# Terraform >= 1.5, AWS provider ~> 5.0
# NOTE: Update the TODOs before applying.
############################################################

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

########################
# Variables
########################
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1" # TODO: change if needed
}

variable "project" {
  description = "A short name used to tag and name resources"
  type        = string
  default     = "tf-ec2-alb-rds"
}

variable "ssh_ingress_cidr" {
  description = "Your IP/CIDR allowed to SSH to EC2 (e.g., 1.2.3.4/32)"
  type        = string
  default     = "0.0.0.0/0" # TODO: lock this down!
}

variable "key_name" {
  description = "Existing EC2 key pair to enable SSH"
  type        = string
  default     = "" # TODO: set if you want SSH access
}

variable "db_username" {
  description = "RDS master username"
  type        = string
  default     = "appuser"
}

variable "db_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
  default     = "ChangeMeStrongPassword123!" # TODO: change
}

variable "vpc_cidr" {
  description = "VPC CIDR"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  type        = list(string)
  description = "Public subnet CIDRs (must be in different AZs)"
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnets" {
  type        = list(string)
  description = "Private subnet CIDRs (must match AZ count)"
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

########################
# Networking — VPC
########################
data "aws_availability_zones" "available" {
  state = "available" # Only consider AZs that are available
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true # Required for DNS resolution in VPC
  enable_dns_hostnames = true # Required for public DNS hostnames
  tags = { Name = "${var.project}-vpc" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.project}-igw" }
}

# Public subnets (for ALB + NAT GW)
resource "aws_subnet" "public" {
  for_each = { for idx, cidr in var.public_subnets : idx => cidr }
  vpc_id                  = aws_vpc.main.id
  cidr_block              = each.value
  availability_zone       = data.aws_availability_zones.available.names[tonumber(each.key)] # Distribute across AZs
  map_public_ip_on_launch = true # Auto-assign public IPs
  tags = {
    Name = "${var.project}-public-${each.key}"
    Tier = "public"
  }
}

# Private subnets (for EC2 ASG + RDS)
resource "aws_subnet" "private" {
  for_each = { for idx, cidr in var.private_subnets : idx => cidr }
  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value
  availability_zone = data.aws_availability_zones.available.names[tonumber(each.key)] # Distribute across AZs
  tags = {
    Name = "${var.project}-private-${each.key}"
    Tier = "private"
  }
}

# Public route table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.project}-public-rt" }
}

resource "aws_route" "public_inet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0" # Default route to internet
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "public_assoc" {
  for_each       = aws_subnet.public
  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

# NAT Gateway in first public subnet
resource "aws_eip" "nat" {
  domain = "vpc" # Allocate EIP in VPC scope
  tags   = { Name = "${var.project}-nat-eip" }
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public["0"].id # Place in first public subnet
  tags          = { Name = "${var.project}-nat" }
  depends_on    = [aws_internet_gateway.igw] # Explicit dependency
}

# Private route table (single, routed via NAT)
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.project}-private-rt" }
}

resource "aws_route" "private_nat" {
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0" # Default route via NAT
  nat_gateway_id         = aws_nat_gateway.nat.id
}

resource "aws_route_table_association" "private_assoc" {
  for_each       = aws_subnet.private
  subnet_id      = each.value.id
  route_table_id = aws_route_table.private.id
}

########################
# Security Groups
########################
# ALB SG: allow HTTP/HTTPS from everywhere
resource "aws_security_group" "alb_sg" {
  name        = "${var.project}-alb-sg"
  description = "ALB security group"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  # (Optional) HTTPS listener later if you add certs
  # ingress {
  #   description = "HTTPS"
  #   from_port   = 443
  #   to_port     = 443
  #   protocol    = "tcp"
  #   cidr_blocks = ["0.0.0.0/0"]
  #   ipv6_cidr_blocks = ["::/0"]
  # }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # Allow all outbound traffic
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = { Name = "${var.project}-alb-sg" }
}

# App SG: allow HTTP from ALB; SSH from your IP; egress all
resource "aws_security_group" "app_sg" {
  name        = "${var.project}-app-sg"
  description = "App instances SG"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "HTTP from ALB"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id] # Only allow traffic from ALB
  }

  dynamic "ingress" {
    for_each = var.key_name != "" ? [1] : [] # Only create SSH rule if key_name is set
    content {
      description = "SSH from your IP (set key_name)"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = [var.ssh_ingress_cidr]
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # Allow all outbound traffic
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = { Name = "${var.project}-app-sg" }
}

# RDS SG: allow Postgres from app SG only
resource "aws_security_group" "rds_sg" {
  name        = "${var.project}-rds-sg"
  description = "RDS SG"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Postgres from app SG"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app_sg.id] # Only allow traffic from app instances
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # Allow all outbound traffic
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = { Name = "${var.project}-rds-sg" }
}

########################
# ALB
########################
resource "aws_lb" "alb" {
  name               = "${var.project}-alb"
  internal           = false # Internet-facing ALB
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [for s in aws_subnet.public : s.id] # Distribute across public subnets
  tags               = { Name = "${var.project}-alb" }
}

resource "aws_lb_target_group" "tg" {
  name     = "${var.project}-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  health_check {
    path                = "/" # Health check endpoint
    protocol            = "HTTP"
    matcher             = "200-399" # Consider 2xx/3xx responses healthy
    interval            = 30
    healthy_threshold   = 2
    unhealthy_threshold = 5
    timeout             = 5
  }
  tags = { Name = "${var.project}-tg" }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.alb.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward" # Forward traffic to target group
    target_group_arn = aws_lb_target_group.tg.arn
  }
}

########################
# IAM for EC2 (SSM)
########################
resource "aws_iam_role" "ec2_role" {
  name = "${var.project}-ec2-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = { Service = "ec2.amazonaws.com" } # Allow EC2 to assume this role
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore" # Enable SSM access
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.project}-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

########################
# EC2 — Launch Template + AutoScaling Group
########################
data "aws_ami" "amazon_linux2" {
  owners      = ["137112412989"] # Official Amazon account
  most_recent = true
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"] # Latest Amazon Linux 2 AMI
  }
  filter {
    name   = "state"
    values = ["available"]
  }
}

locals {
  user_data = base64encode(<<-EOF
    #!/bin/bash
    set -eux
    yum update -y
    yum install -y nginx
    systemctl enable nginx
    cat >/usr/share/nginx/html/index.html <<HTML
    <html><body>
    <h1>${var.project} — Hello from $(hostname)</h1>
    <p>ALB -> ASG -> EC2 working.</p>
    <p>RDS endpoint: ${aws_db_instance.db.address}:5432</p>
    </body></html>
    HTML
    systemctl start nginx
  EOF
  ) # User data script to install and configure nginx
}

resource "aws_launch_template" "app" {
  name_prefix   = "${var.project}-lt-"
  image_id      = data.aws_ami.amazon_linux2.id
  instance_type = "t3.micro"
  key_name      = var.key_name != "" ? var.key_name : null # Only set key_name if provided

  iam_instance_profile {
    name = aws_iam_instance_profile.ec2_profile.name # Attach IAM profile for SSM
  }

  network_interfaces {
    security_groups = [aws_security_group.app_sg.id]
    delete_on_termination = true
  }

  user_data = local.user_data # Pass user data script

  tag_specifications {
    resource_type = "instance"
    tags = { Name = "${var.project}-app" }
  }
}

resource "aws_autoscaling_group" "asg" {
  name                      = "${var.project}-asg"
  max_size                  = 3
  min_size                  = 2
  desired_capacity          = 2
  vpc_zone_identifier       = [for s in aws_subnet.private : s.id] # Distribute across private subnets
  health_check_type         = "ELB" # Use ALB health checks
  health_check_grace_period = 90 # Wait 90 sec before checking health

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest" # Always use latest launch template version
  }

  target_group_arns = [aws_lb_target_group.tg.arn] # Register instances with ALB

  tag {
    key                 = "Name"
    value               = "${var.project}-asg"
    propagate_at_launch = true # Propagate tag to instances
  }

  lifecycle {
    ignore_changes = [desired_capacity] # Prevent Terraform from modifying desired capacity
  }

  depends_on = [aws_lb_listener.http] # Ensure ALB is ready before creating ASG
}

########################
# RDS — PostgreSQL
########################
resource "aws_db_subnet_group" "db" {
  name       = "${var.project}-db-subnets"
  subnet_ids = [for s in aws_subnet.private : s.id] # Distribute across private subnets
  tags       = { Name = "${var.project}-db-subnets" }
}

resource "aws_db_instance" "db" {
  identifier              = "${var.project}-pg"
  engine                  = "postgres"
  engine_version          = "15.5"          # Adjust if needed
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  storage_type            = "gp3"
  username                = var.db_username
  password                = var.db_password
  db_subnet_group_name    = aws_db_subnet_group.db.name # Place in private subnets
  vpc_security_group_ids  = [aws_security_group.rds_sg.id] # Only allow app SG access
  publicly_accessible     = false # Disable public access
  multi_az                = false # Single-AZ for demo (enable for prod)
  backup_retention_period = 7
  delete_automated_backups = true
  skip_final_snapshot     = true  # For demos; disable in prod
  tags                    = { Name = "${var.project}-rds" }
}

########################
# Helpful Outputs
########################
output "alb_dns_name" {
  description = "Public DNS of the ALB"
  value       = aws_lb.alb.dns_name
}

output "alb_http_url" {
  description = "Convenient http URL"
  value       = "http://${aws_lb.alb.dns_name}"
}

output "rds_endpoint" {
  description = "RDS endpoint (hostname:port)"
  value       = "${aws_db_instance.db.address}:5432"
  sensitive   = false
}

output "private_subnet_ids" {
  value = [for s in aws_subnet.private : s.id]
}

output "public_subnet_ids" {
  value = [for s in aws_subnet.public : s.id]
}