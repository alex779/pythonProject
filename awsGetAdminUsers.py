import boto3
import json


client = boto3.client('iam')
users = client.list_users()
user_list = []

for key in users['Users']:
    result = {}
    Policies = []
    Groups=[]

    result['userName'] = key['UserName']
    List_of_Policies = client.list_user_policies(UserName=key['UserName'])

    result['Policies'] = List_of_Policies['PolicyNames']

    List_of_Groups = client.list_groups_for_user(UserName=key['UserName'])

    for Group in List_of_Groups['Groups']:
        Groups.append(Group['GroupName'])
    result['Groups'] = Groups
    user_list.append(result)

for key in user_list:
    print (key)
    f = open("venv/users.csv", "a")
    f.write(json.dumps(key) + "\n")
    f.close()
#    with open('users.csv', 'w') as file:
#        file.write(json.dumps(key))