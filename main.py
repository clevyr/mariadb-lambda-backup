import json
from os import environ, mkdir, path, getcwd
from threading import Timer
from time import strftime, gmtime

import inquirer
import boto3 as boto
import hvac
import shutil
import subprocess
import traceback
import sys

s3 = boto.resource("s3")


def exit(error=None):
    if error is not None:
        print('Error occured, sending email...')
        print(error)
        email(error, environ.get('EMAIL_FROM'),
              environ.get('EMAIL_TO').split(';'))


def main():
    try:
        vault_secret = environ.get("VAULT_SECRET")
        bucket_name = environ.get("BUCKET_NAME")
        mysql_host = environ.get("MYSQL_HOST")
        username = environ.get("MYSQL_USERNAME")
        password = environ.get("MYSQL_PASSWORD")
        database = environ.get("MYSQL_DATABASE")

        if mysql_host is None:
            questions = [
                inquirer.Text(
                    'mysql_host', message='What is the host of the Postgres instance?'),
                inquirer.Text(
                    'postgres_database', message='What is the host of the Postgres instance?'),
                inquirer.Text(
                    'username', message='What is the username for postgres?'),
                inquirer.Password(
                    'password', message='What is the password for postgres?'),
            ]
            answers = inquirer.prompt(questions)
            mysql_host = answers['mysql_host']
            database = answers['postgres_database']
            username = answers['username']
            password = answers['password']

        if vault_secret is not None:
            client = hvac.Client(
                url=environ.get('VAULT_HOST'),
                token=environ.get('VAULT_TOKEN')
            )

            try:
                client.renew_token(increment=60 * 60 * 72)
            except hvac.exceptions.InvalidRequest as _:
                # Swallow, as this is probably a root token
                pass
            except hvac.exceptions.Forbidden as _:
                # Swallow, as this is probably a root token
                pass
            except Exception as e:
                exit(e)

            secret = client.read(vault_secret)['data']
            username = secret['username']
            password = secret['password']
            database = secret['database']

        filename = "/tmp/backup-{}.sql.gz".format(
            strftime("%Y-%m-%d_%H%M%S", gmtime()))

        return_code = None
        with open(filename, 'w') as backup:
            mysqldump_process = subprocess.Popen(
                ['/usr/bin/mysqldump', '-h', mysql_host, '-u', username, database],
                stdout=subprocess.PIPE,
                env={'MYSQL_PWD': password})

            gzip_process = subprocess.Popen(['gzip', '-f'], stdin=mysqldump_process.stdout, stdout=backup)

            return_code = gzip_process.wait()

        if return_code != 0:
            exit(return_code)

        if bucket_name is not None:
            s3.Bucket(bucket_name).upload_file(
                filename, path.basename(filename))
        else:
            print(f"Backup is available at {filename}")
        print("Done")
        exit()
    except Exception as e:
        exit(e)


def email(error, from_address, addresses):
    try:
        ses = boto.client('ses', region_name=environ.get('SES_REGION'))
        bucket_name = environ.get('BUCKET_NAME')
        errString = ''.join(traceback.format_exception(
            etype=type(error), value=error, tb=error.__traceback__))
        response = ses.send_email(
            Source=from_address,
            Destination={
                'ToAddresses': addresses
            },
            Message={
                'Subject': {
                    'Data': 'Error: Backup Failed'
                },
                'Body': {
                    'Text': {
                        'Data': f'The database backup for {bucket_name} failed:\n{errString}'
                    }
                }
            }
        )
    except Exception as e:
        print('Error sending email...')
        print(e)


if __name__ == "__main__":
    main()


def lambda_handler(_, __):
    main()
