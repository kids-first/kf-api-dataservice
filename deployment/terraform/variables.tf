variable "domain_external" {
  description = "The external domain name"
  default     = "kidsfirstdrc.org"
}

variable "prefix_list_ids" {
  type        = list(string)
  description = "The prefix list"
  default     = []
}

variable "create_service_discovery" {
  description = "Create service discovery for the application"
  default     = "0"
}

variable "app_sg_name" {
  description = "Outside application security group name. Please specify a name of another application that would be able to connect to task directly bypassing alb. The communication will work only within VPC."
  default     = ""
}

variable "schedule" {
  description = "Backup schedule for efs"
  default     = "cron(15 * ? * * *)"
}

variable "cold_storage_after" {
  description = "Specifies the number of days after creation that a recovery point is moved to cold storage"
  default     = "1"
}

variable "delete_after" {
  description = "Specifies the number of days after creation that a recovery point is deleted. Must be 90 days greater than cold_storage_after"
  default     = "91"
}

variable "health_check_protocol" {
  description = "Health Check Protocol (HTTP, HTTPS, TCP etc.). Please refer to https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_target_group#protocol"
  default     = "HTTP"
}

variable "container_protocol" {
  description = "Container Protocol (HTTP, HTTPS, etc)"
  default     = "HTTP"
}

variable "secrets_location" {
  description = "Location of secrets in S3"
  default     = ""
}

variable "friendly_dns_name" {
  description = "Friendly-looking DNS name"
  default     = "dataservice"
}

variable "additional_ssl_cert_domain_name" {
  description = "Additional ssl that needs to be attached to the ALB: *.kf-strides.org"
  default     = "*.kidsfirstdrc.org"
}

variable "idle_timeout" {
  description = "Idle timeout for target group"
  default     = 300
}

variable "enable_alb_auth" {
  description = "Enable ALB auth"
  default     = 0
}

variable "enable_waf" {
  description = "Enable WAF"
  default     = 0
}

variable "alb_stickiness_enabled" {
  description = "Enable ALB stickiness"
  default     = false
}

variable "alb_stickiness_cookie_duration" {
  description = "Duration when the cookie will be valid for ALB stickiness"
  default     = "300"
}

variable "create_default_iam_role" {
  description = "Create default IAM role"
  default     = 1
}

variable "azs" {
  description = "Availability zones where the ALB and the service will be available"
  type        = list(any)
  default     = ["a", "b", "c", "e"]
}

variable "create_cloudwatch_log_group" {
  description = "Create cloudwatch log group"
  default     = 1
}

variable "create_ecr" {
  description = "Create ECR"
  default     = 0
}

variable "additional_security_groups" {
  description = "Additional Security Groups"
  default     = ""
}

variable "vpc_prefix" {
  description = "VPC prefix"
  default     = "apps"
}

variable "cluster_prefix" {
  description = "Cluster prefix"
  default     = "apps"
}

variable "subnet_prefix" {
  description = "Subnet prefix"
  default     = "apps"
}

variable "service_name" {
  description = "Service Name"
  default     = "default"
}

variable "launch_type" {
  description = "Launch type"
  default     = "FARGATE"
}

variable "environment" {
  description = "Environment that application is deployed to."
}

variable "application" {
  description = "Application name"
  default     = "kf-api-dataservice"
}

variable "organization" {
  description = "Organization"
  default     = "kf"
}

variable "region" {
  description = "Region the application is being deployed to"
  default     = "us-east-1"
}

variable "chop_cidr" {
  description = "CIDR to allow to access an application"
  type        = list(string)
}

variable "owner" {
  description = "Owner of the application"
  default     = "kf-strides"
}

variable "image_tag" {
  description = "Docker image full name"
}

variable "task_role_arn" {
  description = "DEPRECIATED: Task role arn"
  default     = ""
}

variable "allow_http_connection" {
  description = "Allow http connection"
  default     = "1"
}

variable "create_sns_topic" {
  description = "Create SNS topic"
  default     = "0"
}

variable "max_ecs_capacity" {
  description = "Maximum capacity of the service"
  default     = "10"
}

variable "min_ecs_capacity" {
  description = "Min capacity of the service"
  default     = "1"
}

variable "max_ecs_capacity_internal" {
  description = "Maximum capacity of the internal service"
  default     = "10"
}

variable "min_ecs_capacity_internal" {
  description = "Minimum capacity of the internal service"
  default     = "1"
}

variable "task_definition" {
  description = "Task definition json formatted string"
  default     = ""
}

variable "vcpu_container" {
  description = "VCPU capacity of an container"
  default     = "512"
}

variable "vcpu_task" {
  description = "VCPU capacity of an task"
  default     = "512"
}

variable "memory_container" {
  description = "Memory capacity of an container"
  default     = "1024"
}

variable "memory_task" {
  description = "Memory capacity of an task"
  default     = "1024"
}

variable "additional_container_ports" {
  description = "Additional container ports to be exposed"
  default     = ""
}

variable "container_port" {
  description = "Primary container port to be exposed"
  default     = "80"
}

variable "internal_cidr" {
  description = "Allow CIDR for ingress traffic for internal application"
  default     = "10.0.0.0/8"
}

variable "application_short" {
  description = "Short name for the application"
  default     = "notset"
}

variable "alarm_memory_threshold" {
  description = "Alarm memory threshold when alarm is triggered"
  default     = "10000000"
}

variable "alarm_cpu_threshold" {
  description = "Alarm CPU threshold when alarm is triggered"
  default     = "75"
}

variable "internal_alb" {
  description = "Provision an internal ALB"
  default     = false 
}

variable "health_check_path" {
  description = "Health check URL path"
  default     = "/"
}

variable "health_check_port" {
  description = "Health check port"
  default     = "traffic-port"
}

variable "health_check_matcher" {
  description = "Health check response code matcher"
  default     = "200"
}

variable "create_additional_internal_alb" {
  description = "Create an additional internal ALB for internal traffic"
  default     = 0
}

variable "desired_count" {
  description = "Desired count for the number of tasks"
  default     = 1
}

variable "desired_count_internal" {
  description = "Desired count for the number of tasks for the internal service"
  default     = 1
}

variable "ecs_autoscaling_target_value" {
  description = "ECS autoscaling target value"
  default     = 60
}

variable "ecs_autoscaling_scale_in_cooldown" {
  description = "ECS authscaling scale in cooldown"
  default     = 300
}

variable "ecs_autoscaling_scale_out_cooldown" {
  description = "ECS autoscaling scale out cooldown"
  default     = 30
}

variable "service_unhealthy_threshold" {
  description = "Service unhealthy threshold"
  default     = 3
}

variable "service_healthy_threshold" {
  description = "Service healthy threshold"
  default     = 3
}

variable "service_timeout" {
  description = "Service timeout period"
  default     = 10
}

variable "service_interval" {
  description = "Service interval period"
  default     = 50
}

variable "domain_internal" {
  description = "Internal domain name"
  default     = "kf-strides.org"
}

variable "create_sqs" {
  description = "Create SQS queue"
  default     = "0"
}

variable "sqs_delay_seconds" {
  description = "SQS delay seconds"
  default     = 0
}

variable "sqs_max_message_size" {
  description = "SQS max message size"
  default     = 2048
}

variable "sqs_message_retention_seconds" {
  description = "SQS message retention seconds"
  default     = 86400
}

variable "sqs_receive_wait_time_seconds" {
  description = "SQS receive wait time seconds"
  default     = 10
}

variable "sqs_visibility_timeout_seconds" {
  description = "SQS visibility timeout seconds"
  default     = 60
}

variable "alb_auth_rule_authorization_endpoint" {
  description = "ALB auth rule authorization endpoint"
  default     = ""
}

variable "alb_auth_rule_client_id" {
  description = "ALB auth rule client id"
  default     = ""
}

variable "alb_auth_rule_client_secret" {
  description = "ALB auth rule client secret"
  default     = ""
}

variable "alb_auth_rule_issuer" {
  description = "ALB auth rule issuer"
  default     = ""
}

variable "alb_auth_rule_token_endpoint" {
  default = "ALB auth rule token endpoint"
}

variable "alb_auth_rule_user_info_endpoint" {
  description = "ALB auth rule user info endpoint"
  default     = ""
}

variable "create_efs" {
  description = "Create EFS volume"
  default     = 0
}

variable "deletion_protection" {
  description = "Enable deletion protection on ALB"
  default     = true
}

variable "efs_container_path" {
  description = "When EFS is enabled, use this to specify mountPoints.containerPath in task definition"
  default     = "/mnt/"
}

variable "entrypoint_command" {
  default = "/app/bin/run.sh"
}

variable "additional_image" {
  default = ""
}

variable "add_cloudfront" {
  default     = 0
  description = "Use cloudfront distribution instead of ALB"
}

variable "cloudfront_prd_domain" {
  default     = ""
  description = "Domain name to use for cloudfront in PRD"
}

variable "cache_policy" {
  default     = "CachingOptimized"
  description = "Name of the Amazon managed caching policy"
}

variable "indexd_url" {
  description = "URL for INDEXD"
}

variable "gen3_url" {
  description = "GEN3 URL"
}
