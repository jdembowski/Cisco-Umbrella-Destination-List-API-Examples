#!/usr/bin/python3

import requests, json, sys

# We need the Umbrella ORG ID here.
api_org = 'XXXXXXX'

# Read the Management API base64 of the management key and secret.
# 
# Key: yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
# Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 
# The Key is located in your Umbrella ORG's dashboard while the secret, once generated cannot
# be recovered.
#
# This can be made with this CLI
# echo -n 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' | openssl base64
#
# Save that output management-api-auth.txt in the same directory as this script.

with open('management-api-auth.txt', 'r') as k:
    api_key = k.read().rstrip()

if len(sys.argv) == 2:
    # If an destination list ID is put on the command line the use that
    dest_list_id = sys.argv[1]
else:
    # If not then list all the available destintion lists IDs and labels.
    print('Please provide a destination list ID')
    print('These IDs are available in your organization')
    print()

    url = 'https://management.api.umbrella.com/v1/organizations/'+api_org+'/destinationlists'

    headers = {
         'accept': 'application/json',
         'authorization': 'basic '+api_key
         }

    response = requests.get(url, headers=headers)

    output=json.loads(response.text)
    # print(json.dumps(output, , sort_keys=True, indent=4))

    if 'statusCode' in output:
        print('No Destination Lists')
    else:
        # print('API call status code:', output['status']['code'])

        dest_lists = []

        for lists in output['data']:
            print('ID:', lists['id'], 'Label:',lists['name'])
            dest_lists.append(lists['id'])

    sys.exit(0)

# Lets take the provided ID and read out the contents.
url = 'https://management.api.umbrella.com/v1/organizations/'+api_org+'/destinationlists/'+dest_list_id+'/destinations/'
headers = {
    'accept': 'application/json',
    'authorization': 'basic '+api_key
}
querystring = {
    'page': '40000',
    'limit': '100'
    }

req = requests.get(url, headers=headers, params=querystring)
output=json.loads(req.text)

total_domains=output['meta']['total']
total_pages = total_domains / 100 + (total_domains % 100)

page = 1

while page <= total_pages:
    querystring = {
        'page': page,
        'limit': '100'
        }
    req = requests.get(url, headers=headers, params=querystring)
    output=json.loads(req.text)
    if 'status' in output:
        for domain in output['data']:
            print(domain['destination'], flush=True)
        page = page + 1

print('{:,}'.format(total_domains),'entries in destination list')
