from datetime import datetime

import boto3
from gvm.connections import TLSConnection
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeTransform
from lxml import etree

# Current date invocation for clones naming
date_now = datetime.today().strftime('%Y-%m-%d')

inv_aws_access_key_id = ''
inv_aws_secret_access_key = ''

bint_aws_access_key_id = ''
bint_aws_secret_access_key = ''

# Inveniam clones naming
inveniam_target_clone_name = 'Inveniam-publicIP - ' + date_now
inveniam_task_clone_name = 'Inveniam - ' + date_now

# Inveniam master instances IDs
inveniam_master_target = 'cd4a395f-c8fb-4781-8eba-e579e298a914'
inveniam_master_task = '090d8c98-90df-44cd-b2ca-c0071ecdf42d'

# Bintel clones naming
bintel_target_clone_name = 'Bintel-publicIP - ' + date_now
bintel_task_clone_name = 'Bintel - ' + date_now

# Bintel master instances IDs
bintel_master_target = 'e884e69a-9dbc-48b6-906c-9244f8d32add'
bintel_master_task = '9de111af-61cf-4e74-b6df-1947bd03f123'

# Establishing connection to OpenVAS
connection = TLSConnection(hostname='54.174.211.146')
transform = EtreeTransform()
with Gmp(connection, transform=transform) as gmp:
    gmp.authenticate('admin', 'admin')


# Getting list of IPs to scan
def get_inv_ip_list():
    session = boto3.Session(aws_access_key_id=inv_aws_access_key_id,
                            aws_secret_access_key=inv_aws_secret_access_key, )
    region = "us-east-1"
    ec2 = session.client('ec2', region_name=region)
    ip_list = []
    ips = ec2.describe_network_interfaces()

    for key in ips['NetworkInterfaces']:
        publicIP = key.get('Association', {}).get('PublicIp')
        if publicIP is not None:
            ip_list.append(publicIP)

    return ip_list


def get_bint_ip_list():
    session = boto3.Session(aws_access_key_id=bint_aws_access_key_id,
                            aws_secret_access_key=bint_aws_secret_access_key, )
    region = "us-east-2"
    ec2 = session.client('ec2', region_name=region)
    ip_list = []
    ips = ec2.describe_network_interfaces()

    for key in ips['NetworkInterfaces']:
        publicIP = key.get('Association', {}).get('PublicIp')
        if publicIP is not None:
            ip_list.append(publicIP)

    return ip_list


#####################################################################################################################

# Cloning master task
def get_inv_task_clone():
    matches = ["Clone", "Inveniam"]
    r = gmp.get_tasks()
    for single_task in r.findall('task'):
        if all(x in single_task.find('name').text for x in matches):
            task_id = single_task.get('id')
            return task_id


# Cloning master target
def get_inv_target_clone():
    matches = ["Clone", "Inveniam"]
    r = gmp.get_targets()
    for single_target in r.findall('target'):
        if all(x in single_target.find('name').text for x in matches):
            target_id = single_target.get('id')
            return target_id


#####################################################################################################################


def get_bint_task_clone():
    matches = ["Clone", "Bintel"]
    r = gmp.get_tasks()
    for single_task in r.findall('task'):
        if all(x in single_task.find('name').text for x in matches):
            task_id = single_task.get('id')
            return task_id


def get_bint_target_clone():
    matches = ["Clone", "Bintel"]
    r = gmp.get_targets()
    for single_target in r.findall('target'):
        if all(x in single_target.find('name').text for x in matches):
            target_id = single_target.get('id')
            return target_id


#####################################################################################################################

# Get the report file
def get_report(t_id):
    reports = gmp.get_reports()
    for single_report in reports.findall('report'):
        if single_report.find('task').get('id') == t_id:
            cloned_report_id = single_report.get('id')
            file = gmp.get_report(cloned_report_id)
            return file


# Run scanner
def run_inveniam_scan():
    # 1) Cloning the master target
    gmp.clone_target(inveniam_master_target)  # Inveniam-publicIP-master

    # 2) Get cloned target ID
    cloned_target_id = get_inv_target_clone()

    # 3) Modifying cloned target -> setting new IPs and name
    gmp.modify_target(target_id=cloned_target_id, name=inveniam_target_clone_name, hosts=get_inv_ip_list())

    # 4) Cloning master task
    gmp.clone_task(inveniam_master_task)  # Inveniam-master

    # 5) Get cloned task ID
    cloned_task_id = get_inv_task_clone()

    # 5) Modifying cloned task -> setting new target and name
    gmp.modify_task(task_id=cloned_task_id, name=inveniam_task_clone_name, target_id=cloned_target_id)

    # 5) Starting cloned task
    # gmp.start_task(task_id=cloned_task_id)


def run_bintel_scan():
    # 1) Cloning the master target
    gmp.clone_target(bintel_master_target)  # Bintel-publicIP-master

    # 2) Get cloned target ID
    cloned_target_id = get_bint_target_clone()

    # 3) Modifying cloned target -> setting new IPs and name
    gmp.modify_target(target_id=cloned_target_id, name=bintel_target_clone_name, hosts=get_bint_ip_list())

    # 4) Cloning master task
    gmp.clone_task(bintel_master_task)  # Bintel-master

    # 5) Get cloned task ID
    cloned_task_id = get_bint_task_clone()

    # 5) Modifying cloned task -> setting new target and name
    gmp.modify_task(task_id=cloned_task_id, name=bintel_task_clone_name, target_id=cloned_target_id)

    # 5) Starting cloned task
    gmp.start_task(task_id=cloned_task_id)


run_inveniam_scan()
#run_bintel_scan()
