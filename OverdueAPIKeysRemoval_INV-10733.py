import sys
import boto3
import time
import os
from botocore.exceptions import ClientError

iam = boto3.client("iam")
user_list = []
max_items = 500


def lambda_handler(event, context):
    print('Listing accounts with API keys last used more than 90 day ago')
    response = iam.list_users(MaxItems=max_items)['Users']
    for user in response:
        username = user['UserName']
        response = iam.list_access_keys(UserName=username)
        for key in response['AccessKeyMetadata']:
            create_date = time.mktime(key['CreateDate'].timetuple())
            now = time.time()
            age = (now - create_date) // 86400
            if key['Status'] == 'Active':
                if age > 90 \
                        and username.partition("@")[2] == "dev.pro" \
                        or username.partition("@")[2] == "dev-pro.net":
                    print("Access key ", key['AccessKeyId'], " for user ", username,
                          " is older than 90 days. Deactivating...")
                    iam.update_access_key(
                        UserName=username,
                        AccessKeyId=key['AccessKeyId'],
                        Status="Inactive"
                    )
                    print("Access key for ", username, " has been deactivated")
                    user_list.append(username)

    RECIPIENTS = {'ToAddresses': user_list}
    SENDER = "no-reply@inveniam.io"
    AWS_REGION = os.environ['region']  # IT-request@inveniam.io
    SUBJECT = "IAM Access Key Rotation"
    BODY_TEXT = \
        ("Your IAM Access Key for <ACCOUNT ID> is expired and has been deactivated.\r\n"
         "Log into AWS and go to your IAM user to rotate API key or re-activate it:"
         " https://console.aws.amazon.com/iam/home?#security_credential")
    BODY_HTML = """
                        Your IAM Access Key need to be rotated in AWS Account: <ACCOUNT ID> as it has expired. 
                        Log into AWS and go to your https://console.aws.amazon.com/iam/home?#security_credential 
                        to create a new set of keys or re-activate the old one. 
                        Ensure to disable / remove your previous key pair in case a new pair is generated.
                                    """
    CHARSET = "UTF-8"
    client = boto3.client('ses', region_name=AWS_REGION)
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': RECIPIENTS,
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
