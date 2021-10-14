import time

import boto3
from botocore.exceptions import ClientError

iam = boto3.client("iam")
user_list = []  # List of users matching the search criteria
max_items = 500  # Maximum number of user accounts to put in a list


def lambda_handler(event, context):
    key_warn()  # Invoke key renewal notification
    key_deactivate()  # Invoke key deactivation
aaaa

def key_warn():
    # This function is checking if the API key age is between 85 and 90 days
    # and sending renewal reminder without any actions with a key
    print('Listing accounts with API keys last used more than 90 day ago')
    response = iam.list_users(MaxItems=max_items)['Users']  # Gathering list of users without specific conditions
    for user in response:
        username = user['UserName']
        response = iam.list_access_keys(UserName=username)  # Gathering access keys
        for key in response['AccessKeyMetadata']:  # Gathering API keys information
            create_date = time.mktime(key['CreateDate'].timetuple())  # Date of API key creation
            now = time.time()  # Actual date
            age = (now - create_date) // 86400  # API age estimation and casting to Number of Days format
            if key['Status'] == 'Active':  # Selection of active API keys
                if (85 < age < 90) \
                        and (username.partition("@")[2] == "dev.pro" or username.partition("@")[2] == "dev-pro.net"):
                    # This function is processing accounts with DevPro emails as a username only
                    print("Access key ", key['AccessKeyId'], " for user ", username,
                          " is expiring. Sending out notification")
                    user_list.append(username)  # Gathering all related accounts in a list

    # Below goes the the email details
    SENDER = "no-reply@inveniam.io"
    AWS_REGION = "us-east-1"
    SUBJECT = "IAM Access Key Rotation"
    BODY_TEXT = \
        ("Your IAM Access Key for <ACCOUNT ID> is expiring in a few days and will be deactivated.\r\n"
         "Log into AWS and go to your IAM user to rotate API key:"
         " https://console.aws.amazon.com/iam/home?#security_credential")
    BODY_HTML = """
                        Your IAM Access Key need to be rotated in AWS Account: <ACCOUNT ID> as it is expiring soon. 
                        Log into AWS and go to your https://console.aws.amazon.com/iam/home?#security_credential 
                        to create a new set of keys. 
                        Ensure to disable / remove your previous key pair in case a new pair is generated.
                                    """
    CHARSET = "UTF-8"
    client = boto3.client('ses', region_name=AWS_REGION)
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': user_list,  # Emails are sent to user that were put in a list before
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


def key_deactivate():
    # This function is checking if the API key age is above 90 days
    # and deactivating (not removing) all corresponding keys with a notification to a user
    print('Listing accounts with API keys last used more than 90 day ago')
    response = iam.list_users(MaxItems=max_items)['Users']  # Gathering list of users without specific conditions
    for user in response:
        username = user['UserName']
        response = iam.list_access_keys(UserName=username)  # Gathering access keys
        for key in response['AccessKeyMetadata']:  # Gathering API keys information
            create_date = time.mktime(key['CreateDate'].timetuple())  # Date of API key creation
            now = time.time()  # Actual date
            age = (now - create_date) // 86400  # API age estimation and casting to Number of Days format
            if key['Status'] == 'Active':  # Selection of active API keys
                if (age > 90) \
                        and (username.partition("@")[2] == "dev.pro" or username.partition("@")[2] == "dev-pro.net"):
                    # This function is processing accounts with DevPro emails as a username only
                    print("Access key ", key['AccessKeyId'], " for user ", username,
                          " is older than 90 days. Deactivating...")
                    iam.update_access_key(  # Deactivating the API key
                        UserName=username,
                        AccessKeyId=key['AccessKeyId'],
                        Status="Inactive"
                    )
                    print("Access key for ", username, " has been deactivated")
                    user_list.append(username)  # Gathering all related accounts in a list

    # Below goes the the email details
    SENDER = "no-reply@inveniam.io"
    AWS_REGION = "us-east-1"
    SUBJECT = "IAM Access Key Rotation"
    BODY_TEXT = \
        ("Your IAM Access Key for <ACCOUNT ID> expired and has been deactivated.\r\n"
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
                'ToAddresses': user_list, # Emails are sent to user that were put in a list before
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
