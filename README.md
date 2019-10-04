# Python mysqldump

[![](https://images.microbadger.com/badges/image/clevyr/mariadb-lambda-backup.svg)](https://microbadger.com/images/clevyr/mariadb-lambda-backup "Get your own image badge on microbadger.com")

This is a Docker-compatible Python script to make a dump of a mariadb database and pushes it to an S3 bucket.

It uses Hashicorp Vault to get the authentication

This is intended to be ran under fargate or a lambda function.

Use lambda if the total database size is less than 256 MB due to disk limitations, otherwise use fargate.

Make sure the lambda or fargate container has IAM access to `s3:PutObject and ses:SendEmail`

## Environment Variables

|    Variable    |                             Details                             |              Example               |
| -------------- | --------------------------------------------------------------- | ---------------------------------- |
| VAULT_SECRET   | the secret to pull from Hashicorp's Vault                       | `secret/testing-mongo`             |
| VAULT_TOKEN    | the token used to access the vault                              | `s.7NaWxclhAr3EE22Z8guUQXw6`       |
| VAULT_HOST     | the vault instance to connect to                                | `https://vault.principle-two.com`  |
| BUCKET_NAME    | The S3 bucket to upload the backup to                           | `p2-dev-backups`                   |
| MYSQL_HOST     | The postgres host to connect to                                 | `3.17.52.25`                       |
| MYSQL_USERNAME | The postgres username to authenticate with                      | `username`                         |
| MYSQL_PASSWORD | The postgres password to authenticate with                      | `password`                         |
| SES_REGION     | The region that SES is working in                               | `us-east-1`                        |
| EMAIL_FROM     | The email address to send emails from                           | `backups@domain.com`               |
| EMAIL_TO       | The list of email addresses to send to, separated by semicolons | `user@domain.com;user1@domain.com` |
| MYSQL_DATABASE | The postgres database to backup                                 | `database_name`                    |
