#!/usr/bin/python3

import requests, json, sys

api_org = 'xxxxxxxx'

with open('management-api-auth.txt', 'r') as k:
    api_key = k.read().rstrip()

if len(sys.argv) == 2:
    dest_list_id = sys.argv[1]
else:
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

# print(json.dumps(output, sort_keys=True, indent=4))

total_domains=output['meta']['total']
total_pages = total_domains / 100 + (total_domains % 100)

# print('{:,}'.format(total_domains),'domains in destination list')
# print('{:,}'.format(total_pages),'pages')

print(json.dumps(output))
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

# print('{:,}'.format(total_domains),'domains in destination list')
