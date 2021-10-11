import os
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

login_profiles_to_remove = []
user_list = []
date_now = datetime.now()
iam_client = boto3.client('iam')
max_idle_days = 90
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

            if difference.days > max_idle_days and username.partition("@")[2] == "dev.pro" \
                    or username.partition("@")[2] == "dev-pro.net":
                login_profiles_to_remove.append(user['UserName'])

                for user_name in login_profiles_to_remove:
                    print('Attempting to remove login profile for {0}'.format(user_name))
                    try:
                        iam_client.delete_login_profile(
                            UserName=user_name
                        )
                        print('User {0} login profile has been removed'.format(user_name))
                        user_list.append(user_name)
                    except ClientError as error:
                        print('An error occurred while deleting login profile.', error)
                        pass

        SENDER = "no-reply@inveniam.io"
        AWS_REGION = "us-east-1"
        SUBJECT = "IAM Password expiration"
        BODY_TEXT = \
            ("Your IAM credentials for <ACCOUNT ID> expired and have been deactivated.\r\n"
             "Please contact IT-request@inveniam.io if you would like to restore access")
        BODY_HTML = """
                            Your IAM credentials for <ACCOUNT ID> expired and have been deactivated.
                            Please contact IT-request@inveniam.io if you would like to restore access"
                    
                                """
        CHARSET = "UTF-8"
        client = boto3.client('ses', region_name=AWS_REGION)
        try:
            response = client.send_email(
                Destination={
                    'ToAddresses': user_list,
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
