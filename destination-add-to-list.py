#!/usr/bin/python3

import requests, json, sys, re

api_org = 'xxxxxxx'

# Get the base64 encoded API combination of 'Your Key:Your Secret' from a file
# This will probably change into the pair and then sent as a requests auth=(Your key, your secret)
# Don't expose your management API pair, you only get one per organization.

with open('management-api-auth.txt', 'r') as k:
    api_key = k.read().rstrip()

url = 'https://management.api.umbrella.com/v1/organizations/'+api_org+'/destinationlists'

headers = {
     'accept': 'application/json',
     'authorization': 'basic '+api_key
     }

response = requests.get(url, headers=headers)

output=json.loads(response.text)
# print(json.dumps(output, indent=4))

if 'statusCode' in output:
    print('No Destination Lists')
else:
    print('API call status code:', output['status']['code'])

    dest_lists = []

    for lists in output['data']:
        print('ID:', lists['id'], 'Label:',lists['name'])
        dest_lists.append(lists['id'])

    # Delete all of the lists. Yeah, don't do this. This just an example and will delete
    # both the Global Allow List and Global Block List.

# These are examples from my demo Umbrella ORG and are not valid
#
# ID: 3487556 Label: Amazing Web Proxy White List
# ID: 3187244 Label: Decrypt STUFF
# ID: 3406070 Label: Do not Decrypt
# ID: 2998044 Label: IP address test
# ID: 2995296 Label: Really Stupidly Big Block List
# ID: 2989292 Label: That's The Way Uh Huh Uh Huh I Don't Like It
# ID: 2989290 Label: That's The Way Uh Huh Uh Huh I Like It
# ID: 3187258 Label: Web Policy Decrypt
# ID: 3176994 Label: Web Proxy Selective URL to block

dst_id = 'xxxxxxx'

payload = "[{\"destination\":\"bad.place.dembowski.net\",\"comment\":\"Because it'sd \"},{\"destination\":\"cnn.com\",\"comment\":\"News site\"}]"

domains = []

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    print('ERROR: please provide an input file name')
    sys.exit(1)

with open(filename) as f:
    domains = f.read().splitlines()

remove_domain = 0

# Make one long list into a list of lists and each list has a number of items.
# Python is cool.

items = 100
domains = [domains[i:i + items] for i in range(0, len(domains), items)]

count = 1
delay_multiplier = 0

for chunk in domains:
    bigdata=[]
    # This is silly.
    bigdata=''
    # The Destination List API doesn't handle json properly so I need to do this hack.
    # This will be reported.

    for domain in chunk:
        # Add valid hostname or domain to json
        # bigdata.append(data)
        # bigdata=bigdata+'{"destination":"'+domain+'","comment":"Not empty becasue 400 error"},'
        bigdata=bigdata+'{"destination":"'+domain+'"},'

    print('Chunk No.:', count, 'in',len(domains))

    # print(json.dumps(bigdata))
    bigdata='['+bigdata[:-1]+']'
    # print(bigdata)

    # Reset the response and make sure we default to borked. Python doesn't have
    # a case statement. Shut up.
    response = 0
    borked = 1

    url = 'https://management.api.umbrella.com/v1/organizations/'+api_org+'/destinationlists/'+dst_id+'/destinations'
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'authorization': 'basic '+api_key
        }
    # req = requests.post(url, data=json.dumps(bigdata), headers=headers)
    borked = 0
    try:
        req = requests.post(url, data=bigdata, headers=headers, timeout=300)
    except requests.exceptions.RequestException as e:
        print(e)
        borked = 1

    if not borked:
        response = req.status_code
        output=json.loads(req.text)
        print('Web Server Status:', response)
        print('App Server Status:', output['status']['code'], output['status']['text'])
        print(json.dumps(output, indent=4))

    if response != output['status']['code']:
        print('Writing to error file')
        error_file = open('error.txt', 'a')
        for domain in chunk:
            error_file.write(domain+'\n')
        error_file.close()

    count=count+1
