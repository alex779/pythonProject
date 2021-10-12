import os
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

login_profiles_to_remove = []
user_list = []
date_now = datetime.now()
iam_client = boto3.client('iam')
max_idle_days = 90
min_idle_days = 85
max_items = 500

res_users = iam_client.list_users(
    MaxItems=max_items
)


def lambda_handler(event, context):
    last_used_date = datetime.now()
    print('Listing accounts with credentials last used more than 90 day ago')

    for user in res_users['Users']:
        if 'PasswordLastUsed' in user:  # Checking for console user password last usage
            last_used_date = user['PasswordLastUsed'].replace(tzinfo=None)
            username = user['UserName']

            difference = date_now - last_used_date

            if (min_idle_days < difference.days < max_idle_days) \
                    and (username.partition("@")[2] == "dev.pro" or username.partition("@")[2] == "dev-pro.net"):
                login_profiles_to_remove.append(user['UserName'])

                for user_name in login_profiles_to_remove:
                    print('Sending password renewal notification to {0}'.format(user_name))
                    user_list.append(user_name)

        RECIPIENTS = {'ToAddresses': user_list}
        SENDER = "no-reply@inveniam.io"
        AWS_REGION = os.environ['region']
        SUBJECT = "IAM Password expiration"
        BODY_TEXT = \
            ("Your Password for <ACCOUNT ID> is expiring in a few days and will be deactivated.\r\n"
             "Log into AWS and go to your IAM user to rotate your password:"
             " https://console.aws.amazon.com/iam/home?#security_credential")
        BODY_HTML = """
                            Your password need to be rotated in AWS Account: <ACCOUNT ID> as it is expiring soon. 
                            Log into AWS and go to your https://console.aws.amazon.com/iam/home?#security_credential 
                            to create a new password. 
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
