import os
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

iam_client = boto3.client('iam')
login_profiles_to_remove = []  # List of users to remove profiles
user_list = []  # List of users matching the search criteria
date_now = datetime.now()  # Current date
max_idle_days = 90  # Maximum possible last used date for credentials
min_idle_days = 85  # Number of idle days to send notification after
max_items = 500  # Maximum number of user accounts to put in a list

res_users = iam_client.list_users(
    MaxItems=max_items
)


def lambda_handler(event, context):
    cred_warn()  # Invoking credentials warning notification
    cred_removal()  # Invoking credentials (login profile) removal


def cred_warn():
    # This function is checking whether last date password was used within specified range - 85-90 days
    print('Listing accounts with credentials last used more than 90 day ago')

    for user in res_users['Users']:
        if 'PasswordLastUsed' in user:  # Checking for console user password last usage
            # Gathering list of users without specific conditions
            last_used_date = user['PasswordLastUsed'].replace(tzinfo=None)
            username = user['UserName']

            # Estimating number of days between current date and last used date for credentials
            difference = date_now - last_used_date

            if (min_idle_days < difference.days < max_idle_days) \
                    and (username.partition("@")[2] == "dev.pro" or username.partition("@")[2] == "dev-pro.net"):
                # This function is processing accounts with DevPro emails as a username only
                login_profiles_to_remove.append(user['UserName'])  # Collecting all accounts that meet the conditions

                for user_name in login_profiles_to_remove:
                    print('Sending password renewal notification to {0}'.format(user_name))
                    user_list.append(user_name)  # Gathering all related accounts in a list to send notifications

        # Below goes the the email details
        SENDER = "no-reply@inveniam.io"
        AWS_REGION = "us-east-1"
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


def cred_removal():
    # This function is checking whether last date password was used below the limit - 90 days,
    # and removing login profile (not profile itself) with a notification to user
    print('Listing accounts with credentials last used more than 90 day ago')

    for user in res_users['Users']:
        if 'PasswordLastUsed' in user:  # Checking for console user password last usage
            last_used_date = user['PasswordLastUsed'].replace(tzinfo=None)
            username = user['UserName']

            # Estimating number of days between current date and last used date for credentials
            difference = date_now - last_used_date

            if (difference.days > max_idle_days) and (username.partition("@")[2] == "dev.pro"
                                                      or username.partition("@")[2] == "dev-pro.net"):
                # This function is processing accounts with DevPro emails as a username only
                login_profiles_to_remove.append(user['UserName'])  # Collecting all accounts that meet the conditions

                for user_name in login_profiles_to_remove:
                    print('Attempting to remove login profile for {0}'.format(user_name))
                    try:
                        iam_client.delete_login_profile(  # Attempting to remove login profile for matching account
                            UserName=user_name
                        )
                        print('User {0} login profile has been removed'.format(user_name))
                        user_list.append(user_name)  # Gathering all related accounts in a list to send notifications
                    except ClientError as error:
                        print('An error occurred while deleting login profile.', error)
                        pass

        # Below goes the the email details
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
