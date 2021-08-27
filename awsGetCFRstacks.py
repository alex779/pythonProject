import boto3
from xlwt import Workbook

session = boto3.Session()
stack_session = session.client('cloudformation')
paginator = stack_session.get_paginator('list_stacks')
response_iterator = paginator.paginate()

wb = Workbook()
sheet1 = wb.add_sheet('Sheet 1')
index = 0

for page in response_iterator:
    stack = page['StackSummaries']
    for output in stack:
        # print('Stack ID: %s' % output['StackId'], 'Stack Name: %s' % output['StackName'], 'Stack Status: %s' %
        # output['StackStatus'], 'Stack description: %s' % output['TemplateDescription']) f = open("stacks.csv",
        # "a") f.write( 'Stack ID: %s' % output['StackId'] + 'Stack Name: %s' % output['StackName'] + 'Stack Status:
        # %s' % output[ 'StackStatus'] + 'Stack description: %s' % output['TemplateDescription'] + "\n") f.close()

        sheet1.write(index, 0, output['StackId'])
        sheet1.write(index, 1, output['StackName'])
        sheet1.write(index, 2, output['StackStatus'])
        sheet1.write(index, 3, output['TemplateDescription'])
        wb.save('stackoverflow.xls')
        index += 1
