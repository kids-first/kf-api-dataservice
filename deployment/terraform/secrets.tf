#########Secrets################
resource "aws_secretsmanager_secret" "secrets" {
  #checkov:skip=CKV2_AWS_57:secret rotation is not configured
  name_prefix                    = "${var.application}/${var.environment}/portal"
  description                    = "Portal Secrets"
  kms_key_id                     = data.aws_kms_key.secretsmanager_key.arn
  force_overwrite_replica_secret = true
  tags = {
    Name = "Portal secrets"
  }
}
resource "aws_secretsmanager_secret_version" "secrets" {
  secret_id = aws_secretsmanager_secret.secrets.id
  secret_string = jsonencode({
    "PG_HOST": "",
    "PG_PORT": "",
    "PG_NAME": "",
    "PG_USER": "",
    "PG_PASS": "", 
    "INDEXD_USER": "",
    "INDEXD_PASS": ""
  })
}

###########IAM POLICY
resource "aws_iam_role_policy" "secrets" {
  name_prefix = "${var.application}-${var.environment}-secrets"
  role        = "ecsTaskExecutionRole-${var.environment}" 
  policy      = data.aws_iam_policy_document.secrets.json
}

data "aws_kms_key" "secretsmanager_key" {
  key_id = "alias/aws/secretsmanager"
}

data "aws_iam_policy_document" "secrets" {
  statement {
    effect = "Allow"

    actions = [
      "secretsmanager:GetSecretValue",
      "kms:Decrypt"
    ]

    resources = [
      aws_secretsmanager_secret.secrets.id,
      data.aws_kms_key.secretsmanager_key.arn
    ]
  }
}


