import boto3
import os
import json
from urllib.parse import unquote_plus

from clean_logs import fix_file

s3_client = boto3.client('s3')


def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        dest_bucket = bucket + '-processed_logs'
        key = unquote_plus(record['s3']['object']['key'])

        download_path = '/tmp'
        download_file = os.path.join(download_path, os.path.basename(key))
        upload_path = '/tmp/processed/'

        s3_client.download_file(bucket, key, download_file)

        lms_instance = key.split('/')[-2]

        keys = fix_file(download_file, upload_path, lms_instance)

        for upload_key in keys:
            print(upload_key)
            s3_client.upload_file(
                os.path.join(upload_path, upload_key),
                dest_bucket,
                os.path.join('logs', upload_key))

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully processed {}'.format(key))
    }
