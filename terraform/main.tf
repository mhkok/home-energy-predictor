module "sg" {
  source  = "terraform-aws-modules/security-group/aws//modules/redshift"
  version = "~> 3.0"

  name   = "dwh-redshift"
  vpc_id = var.vpc_id_euwest

  # Allow ingress rules to be accessed only within current VPC
  ingress_cidr_blocks = var.ingress_cidr_blocks

  # Allow all rules for all protocols
  egress_rules = ["all-all"]
}

module "redshift" {
  source  = "terraform-aws-modules/redshift/aws"
  version = "~> 3.0"

  cluster_identifier      = "dwh-cluster"
  cluster_node_type       = "dc2.large"
  cluster_number_of_nodes = 1

  cluster_database_name   = "dwh"
  cluster_master_username = var.cluster_master_username
  cluster_master_password = var.cluster_master_password

  final_snapshot_identifier = false

  publicly_accessible = true

  # Group parameters
  wlm_json_configuration = "[{\"query_concurrency\": 5}]"

  # DB Subnet Group Inputs
  subnets = ["subnet-22a1097a", "subnet-fc43d88a", "subnet-a6412fc2" ] # US-EAST-1 #"subnet-b54d659d", "subnet-e35f3787", "subnet-2a43c05c"
  vpc_security_group_ids = [module.sg.this_security_group_id]

  # IAM Roles
  cluster_iam_roles = [aws_iam_role.redshift-iam-role.arn]
}

module "sg_airflow" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 3.0"

  name        = "airflow-sg"
  description = "Security group for Airflow"
  vpc_id      = var.vpc_id_euwest

  ingress_with_cidr_blocks = [
  {
      rule        = "ssh-tcp"
      cidr_blocks = "87.214.33.143/32"
  }]

  egress_rules = ["all-all"]
}

module "ec2_instance_airflow" {
  source                 = "terraform-aws-modules/ec2-instance/aws"
  version                = "~> 2.0"

  name                   = "euwest1-airflow-deployment"
  instance_count         = 1

  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t2.medium"
  key_name               = "mhkok.aws.personal"
  monitoring             = true

  associate_public_ip_address = true
  vpc_security_group_ids = [module.sg_airflow.this_security_group_id]
  subnet_id              = tolist(data.aws_subnet_ids.all.ids)[0]

  user_data_base64 = base64encode(local.user_data)
  tags = {
    Environment = "dev"
  }
}

locals {
  user_data = <<EOF
#!/bin/bash
sudo yum update -y
sudo yum install docker -y
sudo yum install -y git
sudo useradd airflow --uid 50000 --gid 0
sudo usermod -a -G docker airflow
sudo usermod -a -G wheel airflow
sudo passwd -d airflow
sudo service docker start
sudo curl -L https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
su - airflow -c "echo -e 'AIRFLOW_UID=50000\nAIRFLOW_GID=0' > .env"
su - airflow -c "curl -L https://raw.githubusercontent.com/mhkok/home-energy-predictor/main/terraform/docker-compose.yaml -o docker-compose.yaml"
su - airflow -c "docker-compose up airflow-init"
su - airflow -c "docker-compose up"
EOF
}