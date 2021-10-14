import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import time

# Turn off certificate warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

accessKey = ""
secretKey = ""
headers = {"Content-type": "application/json", "X-ApiKeys": "accessKey=" + accessKey + "; secretKey=" + secretKey}

# Get fileid and token

scanid = 2844  # Since we already know which scan we want this can be hardcoded for now
scanurl = "https://explorer.dev-pro.net/#/scans/folders/946/" + str(scanid) + "/export"
scanpld = {"format": "nessus"}
results = requests.post(scanurl, headers=headers, data=json.dumps(scanpld), verify=False).json()
scanreq = json.loads(json.dumps(results, indent=2, sort_keys=True))

print(scanreq)

print("Your report is being prepared...")

# Get the status of the file

filestat = requests.get(scanurl + str(scanreq["file"]) + "/status", headers=headers, data=json.dumps(scanreq["token"]),
                        verify=False)

count = 0
while filestat.status_code != 200:
    print("Your report is being prepared..." + str(count) + "/400")
    time.sleep(3)
    filestat = requests.get(scanurl + "/" + str(scanreq["file"]) + "/status", headers=headers,
                            data=json.dumps(scanreq["token"]), verify=False)
    count += 1
    if count > 400:
        print("Your file has not been prepared after 20 minutes. Please try again")
        break
    continue

# This part has not yet been tested

# Download the file

if filestat.status_code == 200:
    requests.get(scanurl + "/" + str(scanreq["file"]) + "/download", headers=headers, data=json.dumps(scanreq["token"]),
                 verify=False)
    print("Your file has been downloaded!")
