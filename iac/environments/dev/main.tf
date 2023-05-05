terraform {
  required_version = ">=1.4.6"
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
  backend "s3" {
    bucket  = "dev-60yfmd-tfstate-s3"
    region  = "ap-northeast-1"
    key     = "terraform.tfstate"
    encrypt = true
  }
}

locals {
  common = {
    env      = "dev"
    app_name = "60yfmd"
    region   = "ap-northeast-1"
  }
}

module "ecr" {
  source = "../../modules/ecr"
  common = {
    app_name = local.common.app_name
    env      = local.common.env
  }
}

module "network" {
  source = "../../modules/network"
  common = local.common
  network = {
    cidr = "172.16.0.0/16"
    public_subnets = [
      {
        az   = "a"
        cidr = "172.16.10.0/24"
      },
      {
        az   = "c"
        cidr = "172.16.20.0/24"
      }
    ]

    private_subnets = [
      {
        az   = "a"
        cidr = "172.16.110.0/24"
      },
      {
        az   = "c"
        cidr = "172.16.210.0/24"
      },
    ]
  }
}

module "ecs" {
  source = "../../modules/ecs"
  common = {
    app_name = local.common.app_name
    env      = local.common.env
  }
  network = {
    vpc_id             = module.network.vpc_id
    private_subnet_ids = module.network.private_subnet_ids
  }
  task = {
    family = "${local.common.env}-${local.common.app_name}-ecs-task"
    cpu    = "8 vCPU"
    memory = "16 GB"
    container_definitions = [
      {
        name      = "${local.common.env}-${local.common.app_name}-container-definition"
        image     = "${module.ecr.repo.repository_url}:latest"
        essential = true
        portMappings = [
          {
            containerPort = 8080,
            hostPort      = 8080,
            protocol      = "tcp"
          },
          {
            containerPort = 8081,
            hostPort      = 8081,
            protocol      = "tcp"
          }
        ]
        command     = []
        entryPoint  = []
        environment = []
        secrets     = []
      }
    ]
  }
}
