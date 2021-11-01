
@Library(value='kids-first/aws-infra-jenkins-shared-libraries', changelog=false) _
ecs_service_type_1_standard {
    projectName = "kf-api-dataservice"
    create_sns_topic = "1"
    create_additional_internal_alb = "1"
    internal_app = "false"
    environments = "dev,qa,prd"
    docker_image_type = "alpine"
    entrypoint_command = "/app/bin/run.sh"
    deploy_scripts_version = "master"
    quick_deploy = "true"
    external_config_repo = "false"
    container_port = "80"
    prd_cidr                   = "10.12.0.0/16"
    vcpu_container             = "2048"
    memory_container           = "4096"
    vcpu_task                  = "2048"
    memory_task                = "4096"
    health_check_path = "/"
    dependencies = "ecr"
    friendly_dns_name = "dataservice"
    additional_ssl_cert_domain_name = "*.kidsfirstdrc.org"
}
