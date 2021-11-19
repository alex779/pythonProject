import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from gvm.connections import TLSConnection
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeTransform
from lxml import etree
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from base64 import b64decode
from pathlib import Path

d = datetime.today().strftime('%Y-%m-%d')

region = "us-east-1"
sws_user = ""
sws_key = ""

client = boto3.client(service_name='ses', region_name=region, aws_access_key_id=sws_user, aws_secret_access_key=sws_key)

inv_pdf_filename = "report_inveniam " + d + ".pdf"
bint_pdf_filename = "report_bintel " + d + ".pdf"


def send_email_inv():
    connection = TLSConnection(hostname='54.174.211.146')
    transform = EtreeTransform()
    with Gmp(connection, transform=transform) as gmp:
        gmp.authenticate('admin', 'admin')

    # Get report

    matches = ["Clone", "Inveniam"]
    r = gmp.get_tasks()
    for single_task in r.findall('task'):
        if all(x in single_task.find('name').text for x in matches):
            task_id = single_task.get('id')
            r = task_id

    reports = gmp.get_reports()
    for single_report in reports.findall('report'):
        if single_report.find('task').get('id') == r:
            cloned_report_id = single_report.get('id')
            response = gmp.get_report(report_id=cloned_report_id,
                                      report_format_id="c402cc3e-b531-11e1-9163-406186ea4fc5")

            report_element = response.find("report")
            content = report_element.find("report_format").tail
            binary_base64_encoded_pdf = content.encode('ascii')
            binary_pdf = b64decode(binary_base64_encoded_pdf)
            pdf_path = Path(inv_pdf_filename).expanduser()
            pdf_path.write_bytes(binary_pdf)

    # Send report
    # et = etree.ElementTree(f)
    # et.write('output.pdf', pretty_print=True)

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = "You can find an actual vulnerability report for {date} in attachment".format(date=d)
    # The HTML body of the email.
    BODY_HTML = """\
    <html>
    <head></head>
    <body>
    <p>You can find an actual vulnerability report for {date} in attachment</p> 
    </body>
    </html>
    """.format(date=d)
    CHARSET = "utf-8"
    # AWS_REGION = "us-east-1"
    # client = boto3.client('ses', region_name=AWS_REGION)
    msg = MIMEMultipart('mixed')
    # Add subject, from and to lines.
    recipients = ['oleksandr.gusiev@dev.pro', 'roman.hanzia@dev.pro']
    msg['Subject'] = 'AWS Public IPs scan result'
    msg['From'] = "no-reply@inveniam.io"
    msg['To'] = ", ".join(recipients)
    msg_body = MIMEMultipart('alternative')
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
    # Add the text and HTML parts to the child container.
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)
    # Define the attachment part and encode it using MIMEApplication.
    att = MIMEApplication(open(inv_pdf_filename, 'rb').read())
    att.add_header('Content-Disposition', 'attachment', filename=inv_pdf_filename)
    if os.path.exists(inv_pdf_filename):
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


def send_email_bint():
    connection = TLSConnection(hostname='54.174.211.146')
    transform = EtreeTransform()
    with Gmp(connection, transform=transform) as gmp:
        gmp.authenticate('admin', 'admin')

    # Get report

    matches = ["Clone", "Bintel"]
    r = gmp.get_tasks()
    for single_task in r.findall('task'):
        if all(x in single_task.find('name').text for x in matches):
            task_id = single_task.get('id')
            r = task_id

    reports = gmp.get_reports()
    for single_report in reports.findall('report'):
        if single_report.find('task').get('id') == r:
            cloned_report_id = single_report.get('id')
            response = gmp.get_report(report_id=cloned_report_id,
                                      report_format_id="c402cc3e-b531-11e1-9163-406186ea4fc5")

            report_element = response.find("report")
            content = report_element.find("report_format").tail
            binary_base64_encoded_pdf = content.encode('ascii')
            binary_pdf = b64decode(binary_base64_encoded_pdf)
            pdf_path = Path(bint_pdf_filename).expanduser()
            pdf_path.write_bytes(binary_pdf)

    # Send report
    # et = etree.ElementTree(f)
    # et.write('output.pdf', pretty_print=True)

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = "You can find an actual vulnerability report for {date} in attachment".format(date=d)
    # The HTML body of the email.
    BODY_HTML = """\
    <html>
    <head></head>
    <body>
    <p>You can find an actual vulnerability report for {date} in attachment</p> 
    </body>
    </html>
    """.format(date=d)
    CHARSET = "utf-8"
    # AWS_REGION = "us-east-1"
    # client = boto3.client('ses', region_name=AWS_REGION)
    msg = MIMEMultipart('mixed')
    # Add subject, from and to lines.
    recipients = ['oleksandr.gusiev@dev.pro', 'roman.hanzia@dev.pro']
    msg['Subject'] = 'AWS Public IPs scan result'
    msg['From'] = "no-reply@inveniam.io"
    msg['To'] = ", ".join(recipients)
    msg_body = MIMEMultipart('alternative')
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
    # Add the text and HTML parts to the child container.
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)
    # Define the attachment part and encode it using MIMEApplication.
    att = MIMEApplication(open(bint_pdf_filename, 'rb').read())
    att.add_header('Content-Disposition', 'attachment', filename=bint_pdf_filename)
    if os.path.exists(bint_pdf_filename):
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


send_email_inv()
# send_email_bint()
