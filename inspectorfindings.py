from datetime import datetime
import boto3

region_name = 'us-east-1'
assessment_run_arn_1 = 'arn:aws:inspector:us-west-2:123456789012:target/0-prsTvjAI/template/0-kXLPD9el/run/0-FhvJqB4l'
max_results = 250000
start_date = datetime(2019, 1, 1)
end_date = datetime(2019, 12, 1)

inspector = boto3.client('inspector', region_name = region_name)
paginator = inspector.get_paginator('list_findings')

finding_filter = {
    'severities': [
        'High',
        'Medium',
        'Low',
        'Informational',
    ],
    'creationTimeRange': {
        'beginDate': start_date,
        'endDate': end_date,
    }
}

for findings in paginator.paginate(
        maxResults=max_results,
        assessmentRunArns=[
            assessment_run_arn_1,
        ],
        filter = finding_filter
    ):
    for finding_arn in findings['findingArns']:
        print(finding_arn)