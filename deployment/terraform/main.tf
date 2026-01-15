data "aws_caller_identity" "current" {}

data "template_file" "task_definition" {
  template = file("definitions/container-definition.json")
  vars = {
    region                   = var.region
    log_group_name           = "apps-${var.environment}/${var.application}"
    image                    = "${data.aws_caller_identity.current.account_id}.dkr.ecr.us-east-1.amazonaws.com/${var.application}:${var.image_tag}"
    environment              = var.environment
    application              = var.application
    task_role_arn            = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.application}-${var.environment}-role"
    additional_image         = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com/${var.additional_image}"
    container_port           = var.container_port
    s3_secrets_bucket_prefix = var.secrets_location == "" ? "${var.organization}-${data.aws_caller_identity.current.account_id}-${var.region}-${var.environment}-secrets/${var.application}" : "${var.organization}-${data.aws_caller_identity.current.account_id}-${var.region}-${var.environment}-secrets/${var.secrets_location}"
    entrypoint_command       = var.entrypoint_command
    memory_container         = var.memory_container
    vcpu_container           = var.vcpu_container
    efs_container_path       = var.efs_container_path
    create_efs               = var.create_efs
  }
}

module "app" {
  source                          = "git@github.com:kids-first/aws-ecs-service-type-1.git?ref=master"
  create_service_discovery        = var.create_service_discovery
  task_definition                 = data.template_file.task_definition.rendered
  region                          = var.region
  additional_container_ports      = var.additional_container_ports
  create_default_iam_role         = var.create_default_iam_role
  create_additional_internal_alb  = var.create_additional_internal_alb
  create_sns_topic                = var.create_sns_topic
  image                           = "${data.aws_caller_identity.current.account_id}.dkr.ecr.us-east-1.amazonaws.com/${var.application}:${var.image_tag}"
  create_sqs                      = var.create_sqs
  create_ecr                      = var.create_ecr
  create_efs                      = var.create_efs
  friendly_dns_name               = var.friendly_dns_name
  create_cloudwatch_log_group     = var.create_cloudwatch_log_group
  internal_alb                    = var.internal_alb
  enable_alb_auth                 = var.enable_alb_auth
  service_name                    = var.application
  environment                     = var.environment
  application                     = var.application
  chop_cidr                       = var.chop_cidr
  owner                           = var.owner
  task_role_arn                   = var.task_role_arn
  container_port                  = var.container_port
  health_check_path               = var.health_check_path
  health_check_port               = var.health_check_port
  health_check_protocol           = var.health_check_protocol
  health_check_matcher            = var.health_check_matcher
  azs                             = var.azs
  domain_internal                 = var.domain_internal
  domain_external                 = var.domain_external
  vpc_prefix                      = var.vpc_prefix
  subnet_prefix                   = var.vpc_prefix
  additional_ssl_cert_domain_name = var.additional_ssl_cert_domain_name
  alb_stickiness_enabled          = var.alb_stickiness_enabled
  secrets_location                = var.secrets_location
  desired_count                   = var.desired_count
  desired_count_internal          = var.desired_count_internal
  min_ecs_capacity                = var.min_ecs_capacity
  max_ecs_capacity                = var.max_ecs_capacity
  app_sg_name                     = var.app_sg_name
  prefix_list_ids                 = var.prefix_list_ids

  memory_task        = var.memory_task
  memory_container   = var.memory_container
  vcpu_container     = var.vcpu_container
  vcpu_task          = var.vcpu_task
  container_protocol = var.container_protocol

  organization                         = var.organization
  alb_auth_rule_authorization_endpoint = var.alb_auth_rule_authorization_endpoint
  alb_auth_rule_client_id              = var.alb_auth_rule_client_id
  alb_auth_rule_client_secret          = var.alb_auth_rule_client_secret
  alb_auth_rule_issuer                 = var.alb_auth_rule_issuer
  alb_auth_rule_token_endpoint         = var.alb_auth_rule_token_endpoint
  alb_auth_rule_user_info_endpoint     = var.alb_auth_rule_user_info_endpoint
  deletion_protection                  = var.deletion_protection
  service_timeout                      = var.service_timeout
  service_interval                     = var.service_interval
  
  cloudfront_prd_domain = var.cloudfront_prd_domain
  add_cloudfront        = var.add_cloudfront
  cache_policy          = var.cache_policy
  enable_waf            = var.enable_waf

  schedule           = var.schedule
  cold_storage_after = var.cold_storage_after
  delete_after       = var.delete_after

  efs_container_path = var.efs_container_path
  entrypoint_command = var.entrypoint_command
  additional_image   = var.additional_image
}
