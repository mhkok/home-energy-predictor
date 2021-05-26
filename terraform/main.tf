module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket        = "p1-staging"
  acl           = "private"
  force_destroy = true

  attach_policy = true
  policy        = data.aws_iam_policy_document.bucket_policy_p1_staging.json

  attach_deny_insecure_transport_policy = true

  tags = {
    Owner = "MK"
  }
}

module "s3_bucket_knmi_weather_data" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket        = "weather-data-staging"
  acl           = "private"
  force_destroy = true

  attach_policy = true
  policy        = data.aws_iam_policy_document.bucket_policy_weather_data.json

  attach_deny_insecure_transport_policy = true

  tags = {
    Owner = "MK"
  }
}

data "aws_iam_policy_document" "bucket_policy_p1_staging" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::315911064428:user/s3-upload-role"]
    }

    actions = [
      "s3:putObject",
    ]

    resources = [
      "arn:aws:s3:::p1-staging/*",
    ]
  }
}


data "aws_iam_policy_document" "bucket_policy_weather_data" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::315911064428:user/s3-upload-role"]
    }

    actions = [
      "s3:putObject",
    ]

    resources = [
      "arn:aws:s3:::weather-data-staging/*",
    ]
  }
}
