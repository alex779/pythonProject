import boto3
import json

client = boto3.client('iam')
users = client.list_users()
user_list = []
userVirtualMfa = client.list_virtual_mfa_devices()
virtualEnabled = []
mfa_users = []

for key in users['Users']:
    result = {}
    Policies = []
    Groups = []

    result['user Name'] = key['UserName']

    userMfa = client.list_mfa_devices(UserName=key['UserName'])

    for uname in userMfa['MFADevices']:
        virtualEnabled.append(uname['UserName'])

    if len(userMfa['MFADevices']) != 0:

        if key['UserName'] in virtualEnabled:
            mfa_users.append(key['UserName'])
            result['MFA'] = 'enabled'
            user_list.append(result)

for key in user_list:
    print(key)
    f = open("users.csv", "a")
    f.write(json.dumps(key) + "\n")
    f.close()
#    with open('users.csv', 'w') as file:
#        file.write(json.dumps(key))
