# IAM roles assumed by this repo's GitHub Actions workflow
# (.github/workflows/deploy.yml) through OIDC.
#
# The OIDC provider is account-wide and lives in the shared aws-infra repo.
# Each role trusts only tokens whose sub claim names this repo and either a
# branch (readonly) or the GitHub environment prod (deploy). The prod
# environment requires approval, so the deploy role is unusable until a run on
# main is approved.
#
# Adapted from njmunicipalities-api/infra/github/. This project has a single
# layer and no dev environment, so there is one deploy role.

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

locals {
  account = data.aws_caller_identity.current.account_id
  region  = data.aws_region.current.region

  oidc_host = "token.actions.githubusercontent.com"

  # The layer itself (publish, list versions) and its versions (get)
  layer_arn          = "arn:aws:lambda:${local.region}:${local.account}:layer:${var.layer_name}"
  layer_version_arns = "${local.layer_arn}:*"

  # The state of ../
  state_key_arn = "arn:aws:s3:::${var.state_bucket}/${var.project}/prod.tfstate"

  # Terraform's reads of aws_lambda_layer_version (plan and refresh)
  layer_read_actions = [
    "lambda:GetLayerVersion",
    "lambda:ListLayerVersions",
  ]
}

# --- readonly ---
# terraform plan on dev and main, so it must not be able to change anything.

data "aws_iam_policy_document" "readonly_trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_host}:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_host}:sub"
      values = [
        "repo:${var.github_repo}:ref:refs/heads/dev",
        "repo:${var.github_repo}:ref:refs/heads/main",
      ]
    }
  }
}

data "aws_iam_policy_document" "readonly" {
  statement {
    sid       = "PlanLayer"
    actions   = local.layer_read_actions
    resources = [local.layer_arn, local.layer_version_arns]
  }

  # terraform plan -lock=false: reads state, never writes the lock file
  statement {
    sid       = "ReadState"
    actions   = ["s3:GetObject"]
    resources = [local.state_key_arn]
  }

  statement {
    sid       = "ListState"
    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::${var.state_bucket}"]

    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["${var.project}/*"]
    }
  }
}

resource "aws_iam_role" "readonly" {
  name               = "${var.project}-gha-readonly"
  assume_role_policy = data.aws_iam_policy_document.readonly_trust.json
}

resource "aws_iam_role_policy" "readonly" {
  name   = "readonly"
  role   = aws_iam_role.readonly.id
  policy = data.aws_iam_policy_document.readonly.json
}

# --- deploy ---
# terraform apply: publishes a new layer version. There is deliberately no
# lambda:DeleteLayerVersion, so published versions (which consumers pin) can't
# be removed from here; the layer uses skip_destroy for the same reason.

data "aws_iam_policy_document" "deploy_trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_host}:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_host}:sub"
      values   = ["repo:${var.github_repo}:environment:prod"]
    }
  }
}

data "aws_iam_policy_document" "deploy" {
  statement {
    sid       = "TerraformLayer"
    actions   = concat(local.layer_read_actions, ["lambda:PublishLayerVersion"])
    resources = [local.layer_arn, local.layer_version_arns]
  }

  statement {
    sid = "TerraformState"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
    ]
    resources = [
      local.state_key_arn,
      "${local.state_key_arn}.tflock",
    ]
  }

  statement {
    sid       = "TerraformListState"
    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::${var.state_bucket}"]

    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["${var.project}/*"]
    }
  }
}

resource "aws_iam_role" "deploy" {
  name               = "${var.project}-gha-deploy-prod"
  assume_role_policy = data.aws_iam_policy_document.deploy_trust.json
}

resource "aws_iam_role_policy" "deploy" {
  name   = "deploy"
  role   = aws_iam_role.deploy.id
  policy = data.aws_iam_policy_document.deploy.json
}
