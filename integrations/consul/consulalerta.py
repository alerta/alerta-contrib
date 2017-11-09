#!/usr/bin/env python

from alertaclient.api import Client
import sys
import os
import time
import json
import consul
import time

client = consul.Consul(host='127.0.0.1', port=8500, token=None, scheme='http', consistency='default', dc=None, verify=True)

j = json.load(sys.stdin)
print "Request:"
print j

try:
    url = client.kv.get('alerta/apiurl')[1]['Value']
except:
    print "No URL defined, exiting"
    sys.exit(1)

try:
    key = client.kv.get('alerta/apikey')[1]['Value']
except:
    print "No key defined, exiting"
    sys.exit(1)


try:
    max_retries = int(client.kv.get('alerta/max_retries')[1]['Value'])
except TypeError:
    print "No value defined, using default"
    max_retries = 3

try:
    sleep = int(client.kv.get('alerta/sleep')[1]['Value'])
except TypeError:
    print "No value defined, using default"
    sleep = 2

try:
    timeout = int(client.kv.get('alerta/timeout')[1]['Value'])
except TypeError:
    print "No value defined, using default"
    timeout = 900

try:
    origin = client.kv.get('alerta/origin')[1]['Value']
except TypeError:
    print "No value defined, using default"
    origin = "consul"

try:
    alerttype = client.kv.get('alerta/alerttype')[1]['Value']
except TypeError:
    print "No value defined, using default"
    alerttype = "ConsulAlert"


api = Client(endpoint=url, key=key)

SEVERITY_MAP = {
    'critical':   'critical',
    'warning':    'warning',
    'passing':    'ok',
}

def createalert( data ):
    try:
        environment = client.kv.get('alerta/env/{0}'.format(data['Node']))[1]['Value']
    except:
        try:
             environment = client.kv.get('alerta/defaultenv')[1]['Value']
        except:
             environment = "Production"

    for i in range(max_retries):
        try:
            print("Response:")
            response = api.send_alert(
              resource=data['Node'],
              event=data['CheckId'],
              value=data['Status'],
              correlate=SEVERITY_MAP.keys(),
              environment=environment,
              service=[data['CheckId']],
              severity=SEVERITY_MAP[data['Status']],
              text=data['Output'],
              timeout=timeout,
              origin=origin,
              type=alerttype
            )
            print(response)
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
