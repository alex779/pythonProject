import boto3
import sys
import time


def cleanup(user, iam_client):
    response = iam_client.list_access_keys(UserName=user)
    for key in response['AccessKeyMetadata']:
        create_date = time.mktime(key['CreateDate'].timetuple())
        now = time.time()
        age = (now - create_date) // 86400
        if age > 90:
            print("AK [", key['AccessKeyId'], "] for user [", user, "] is older than 90 days. Deleting...")
            response = iam_client.delete_access_key(
                UserName=user,
                AccessKeyId=key['AccessKeyId']
            )

    # Check if user has password profile
    try:
        response = iam_client.get_login_profile(UserName=user)
    except Exception as e:
        if 'NoSuchEntity' not in str(e):
            raise
    else:
        print("User [", user, "] has password profile. Deleting..")
        response = iam_client.delete_login_profile(UserName=user)


def handler(event, context):
    iam_client = boto3.client('iam')
    user_list = []
    group_list = []
    whitelist_group_name = "automation-users"

    response = iam_client.list_groups()
    for item in response['Groups']:
        group_list.append(item['GroupName'])

    if whitelist_group_name not in group_list:
        print("Automation Users Group Doesn't Exist! Script Exiting.")
        sys.exit(1)

    response = iam_client.list_users()
    print("----------------------------------------------")
    for item in response['Users']:
        user = item['UserName']
        is_automation_user = False
        user_list.append(user)
        response = iam_client.list_groups_for_user(UserName=user)
        if response['Groups']:
            for group in response['Groups']:
                if group['GroupName'] == whitelist_group_name:
                    print("User [", user, "] is an automation-user. Won't be touched.")
                    is_automation_user = True
        if is_automation_user:
            print("----------------------------------------------")
            continue
        else:
            print("User [", user, "] is a regular user. Checking credentials..")
            cleanup(user, iam_client)
            print("Cleanup on user [", user, "] is now complete.")
        print("----------------------------------------------")
