data "aws_route53_zone" "kf-strides" {
  name = "kf-strides.org"  # Replace with your zone name
}

resource "aws_route53_record" "kf-api-dataservice" {
  zone_id = data.aws_route53_zone.kf-strides.zone_id 
  name    = var.environment != "prd" ? "kf-api-dataservice-${var.environment}" : "kf-api-dataservice"
  type    = "CNAME"
  ttl     = 300
  records = [module.app.alb_dns_name]
}
