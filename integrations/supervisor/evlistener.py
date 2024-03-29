#!/usr/bin/env python

import json
import platform
import sys

from alertaclient.api import Client


class Listener:

    def wait(self):
        data = sys.stdin.readline()
        headers = dict([x.split(':') for x in data.split()])
        data = sys.stdin.read(int(headers['len']))
        body = dict([x.split(':') for x in data.split()])
        return headers, body

    def send_cmd(self, s):
        sys.stdout.write(s)
        sys.stdout.flush()

    def log_stderr(self, s):
        sys.stderr.write(s)
        sys.stderr.flush()


def main():

    api = Client()
    listener = Listener()

    while True:
        listener.send_cmd('READY\n')
        headers, body = listener.wait()
        event = headers['eventname']

        if event.startswith('TICK'):
            try:
                origin = '{}/{}'.format('supervisord', platform.uname()[1])
                api.heartbeat(origin, tags=[headers['ver'], event])
            except Exception as e:
                listener.log_stderr(e)
                listener.send_cmd('RESULT 4\nFAIL')
            else:
                listener.send_cmd('RESULT 2\nOK')
        else:
            if event.endswith('FATAL'):
                severity = 'critical'
            elif event.endswith('BACKOFF'):
                severity = 'warning'
            elif event.endswith('EXITED'):
                severity = 'minor'
            else:
                severity = 'normal'
            try:
                api.send_alert(
                    resource='{}:{}'.format(
                        platform.uname()[1], body['processname']),
                    environment='Production',
                    service=['supervisord'],
                    event=event,
                    correlate=[
                        'PROCESS_STATE_STARTING',
                        'PROCESS_STATE_RUNNING',
                        'PROCESS_STATE_BACKOFF',
                        'PROCESS_STATE_STOPPING',
                        'PROCESS_STATE_EXITED',
                        'PROCESS_STATE_STOPPED',
                        'PROCESS_STATE_FATAL',
                        'PROCESS_STATE_UNKNOWN'
                    ],
                    value='serial=%s' % headers['serial'],
                    severity=severity,
                    origin=headers['server'],
                    text='State changed from {} to {}.'.format(
                        body['from_state'], event),
                    raw_data='{}\n\n{}'.format(
                        json.dumps(headers), json.dumps(body))
                )
            except Exception as e:
                listener.log_stderr(e)
                listener.send_cmd('RESULT 4\nFAIL')
            else:
                listener.send_cmd('RESULT 2\nOK')


if __name__ == '__main__':
    main()
