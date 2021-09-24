from datetime import date

import boto3
import datetime
import json

iam = boto3.client('iam')
user_list = []
currentDate = date.today()

for userList in iam.list_users()['Users']:
    userKeys = iam.list_access_keys(UserName=userList['UserName'])
    for keyValue in userKeys['AccessKeyMetadata']:
        if keyValue['Status'] == 'Active':
            username = keyValue['UserName']
            active_days = currentDate - keyValue['CreateDate'].date()
            if active_days >= datetime.timedelta(days=90) \
                    and username.partition("@")[2] == "dev.pro" \
                    or username.partition("@")[2] == "dev-pro.net":
                result = {'User Name': keyValue['UserName'],
                          'Key Age': str(active_days),
                          'Access key ID': keyValue['AccessKeyId']}
                # userKeys = iam.delete_access_key(  # Remove found overdue access keys
                #     UserName=username,
                #     AccessKeyId=keyValue['AccessKeyId']
                # )
                user_list.append(result)  # Gather finding to a list
                print(active_days)

for key in user_list:
    print(key)
    f = open("apiKeys.csv", "a")
    f.write(json.dumps(key) + "\n")
    f.close()