import boto3
import json
from datetime import datetime

iam = boto3.client('iam')
userlist = iam.list_users()['Users']
current_date = datetime.now()
max_idle_days = 90
user_list = []

for key in userlist:
    username = key['UserName']
    if 'PasswordLastUsed' in key:  # Checking for console user password last usage
        last_used_date = key['PasswordLastUsed'].replace(tzinfo=None)

        difference = current_date - last_used_date
        if difference.days > max_idle_days \
                and (username.partition("@")[2] == "dev.pro" or username.partition("@")[2] == "dev-pro.net"):
            print(username + ' - ' + str(difference))
            result = {'Username': username, 'Last used (days ago)': difference}
            user_list.append(result)

for key in user_list:
    f = open("unusedCreds.cdv", "a")
    f.write(json.dumps(key) + "\n")
    f.close()
