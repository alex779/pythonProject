import boto3
from botocore.exceptions import ClientError

boto3.setup_default_session(profile_name='default')

s3 = boto3.client('s3')
response = s3.list_buckets()

for bucket in response['Buckets']:
    try:
        enc = s3.get_bucket_encryption(Bucket=bucket['Name'])
        rules = enc['ServerSideEncryptionConfiguration']['Rules']
        print('Bucket: %s, Encryption: %s' % (bucket['Name'], rules))
        f = open("venv/encbuckets.csv", "a")
        f.write('%s, Encryption: %s' % (bucket['Name'], rules) + "\n")
        f.close()
    except ClientError as e:
        if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
            print('Bucket: %s, no server-side encryption' % (bucket['Name']))
            f = open("venv/encbuckets.csv", "a")
            f.write('%s, no server-side encryption' % (bucket['Name']) + "\n")
            f.close()
        else:
            print("Bucket: %s, unexpected error: %s" % (bucket['Name'], e))
