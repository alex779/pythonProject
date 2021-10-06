import json
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3
from botocore.exceptions import ClientError

# session = boto3.Session(profile_name='bintel')
# region = "us-east-2"
# ec2 = session.client('ec2', region_name=region)
# response = ec2.describe_network_interfaces()

ec2 = boto3.client('ec2')

ip_list = []
ips = ec2.describe_network_interfaces()


def lambda_handler(event, context):
    for key in ips['NetworkInterfaces']:
        publicIP = key.get('Association', {}).get('PublicIp')
        if publicIP is not None:
            ip_list.append(publicIP)

    for key in ip_list:
        f = open("/tmp/ips.csv", "a")
        f.write(json.dumps(key) + "\n")
        f.close()

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = "Hello,\r\nPlease review the actual list of Public IP addresses " \
                "that associated with Inveniam AWS account (ID: 800161095412)"
    # The HTML body of the email.
    BODY_HTML = """\
    <html>
    <head></head>
    <body>
    <h1>Hello!</h1>
    <p>Please review the actual list of Public IP addresses 
    that associated with Inveniam AWS account (ID: 800161095412)</p>
    </body>
    </html>
    """
    CHARSET = "utf-8"
    AWS_REGION = "us-east-1"
    client = boto3.client('ses', region_name=AWS_REGION)
    msg = MIMEMultipart('mixed')
    # Add subject, from and to lines.
    recipients = ['oleksandr.gusiev@dev.pro', 'roman.hanzia@dev.pro']
    msg['Subject'] = 'Bintel IP discovery'
    msg['From'] = "no-reply@inveniam.io"
    msg['To'] = ", ".join(recipients)
    msg_body = MIMEMultipart('alternative')
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
    # Add the text and HTML parts to the child container.
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)
    # Define the attachment part and encode it using MIMEApplication.
    att = MIMEApplication(open('/tmp/ips.csv', 'rb').read())
    att.add_header('Content-Disposition', 'attachment', filename="ips.csv")
    if os.path.exists('/tmp/ips.csv'):
        print("File exists")
    else:
        print("File does not exists")
    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container.
    msg.attach(msg_body)
    # Add the attachment to the parent container.
    msg.attach(att)
    try:
        # Provide the contents of the email.
        response = client.send_raw_email(
            Source=msg['From'],
            Destinations=recipients,
            RawMessage={
                'Data': msg.as_string(),
            }
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        return e.response['Error']['Message']
    else:
        return "Email sent! Message ID:", response['MessageId']
