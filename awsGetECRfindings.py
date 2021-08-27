import boto3
import json

client = boto3.client('ecr')
findings_list = []

response = client.describe_image_scan_findings(
    registryId='472345033518',
    repositoryName='elasticsearch_proxy',
    imageId={
        'imageTag': 'latest'
    },
)

findings = response['imageScanFindings']['findings']
for key in findings:

    if key['severity'] == "HIGH":  # or finding['severity'] == "MEDIUM" or finding['severity'] == "LOW":
        result = {}
        result['Finding name'] = key['name']
        result['Finding Description'] = key['description']
        result['Finding Severity'] = key['severity']
        # results.append(finding['name'] + finding['description'] + finding['severity'])
        findings_list.append(result)
        print(key)
        print(result)

for key in findings_list:
    print(key)
    f = open("results.csv", "a")
    f.write(json.dumps(key) + "\n")
    f.close()
