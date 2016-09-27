#!/usr/bin/env python

from alertaclient.api import ApiClient
from alertaclient.alert import Alert
import sys
import os
import time
import json
import consul
import time

client = consul.Consul(host='127.0.0.1', port=8500, token=None, scheme='http', consistency='default', dc=None, verify=True)

j = json.load(sys.stdin)
print j

url = client.kv.get('alerta/apiurl')[1]['Value']
key = client.kv.get('alerta/apikey')[1]['Value']

max_retries = int(client.kv.get('alerta/max_retries')[1]['Value'])
sleep = int(client.kv.get('alerta/sleep')[1]['Value'])
timeout = int(client.kv.get('alerta/timeout')[1]['Value'])

origin = client.kv.get('alerta/origin')[1]['Value']
alerttype = client.kv.get('alerta/alerttype')[1]['Value']

event = 'Problem'
value = 'Error'

api = ApiClient(endpoint=url, key=key)


SEVERITY_MAP = {
    'critical':   'critical',
    'warning':    'warning',
    'passing':    'ok',
}

def createalert( data ):
    try:
        environment = client.kv.get('alerta/env/{0}'.format(data['Node']))[1]['Value']
    except:
        environment = client.kv.get('alerta/defaultenv')[1]['Value']
    alert = Alert(resource=data['Node'], event=[data['CheckId']], environment=environment, service=[data['CheckId']], severity=SEVERITY_MAP[data['Status']], text=data['Output'], value=value, timeout=timeout, origin=origin, type=alerttype)
    for i in range(max_retries):
        try:
            print(api.send(alert))
        except Exception as e:
            print("HTTP Error: {}".format(e))
            time.sleep(sleep)
            continue  
        else:
            break
    else:
        print("api is down")

def main():
    for item in enumerate(j):
        i=item[0]
        createalert(j[i])

if __name__ == "__main__":
    main()
