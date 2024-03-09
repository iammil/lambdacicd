import boto3

def download_file_from_s3():
    s3_client = boto3.client('s3', region_name='ap-southeast-1')
    bucket_name = 'principalbucketmil'
    file_key = 'db/medcury-de.db'
    s3_client.download_file(bucket_name, file_key,'/tmp/edcury-de.db')

def upload_file_to_s3():
    s3_client = boto3.client('s3', region_name='ap-southeast-1')
    bucket_name = 'principalbucketmil'
    file_key = 'dbnew/medcury-de.db'
    local_path = '/tmp/edcury-de.db'
    s3_client.upload_file(local_path, bucket_name, file_key)