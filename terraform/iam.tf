resource "aws_iam_role" "redshift-iam-role" {
  name = "redshift-iam-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "redshift.amazonaws.com",
        "AWS": "arn:aws:iam::315911064428:user/matthijs.kok"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "s3_fullaccess_attach" {
  role       = aws_iam_role.redshift-iam-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}
