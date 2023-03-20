import json
import logging
import os
import urllib

import requests
from alerta.plugins import PluginBase

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0


LOG = logging.getLogger('alerta.plugins.matrix')

MATRIX_HOMESERVER_URL = [
    os.environ.get('MATRIX_HOMESERVER') or app.config['MATRIX_HOMESERVER'],
    '/_matrix/client/r0/rooms/',
    urllib.parse.quote(os.environ.get('MATRIX_ROOM')
                       or app.config['MATRIX_ROOM'], ':'),  # noqa: W503
    '/send/m.room.message'
]
MATRIX_ACCESS_TOKEN = os.environ.get(
    'MATRIX_ACCESS_TOKEN') or app.config['MATRIX_ACCESS_TOKEN']
MATRIX_MESSAGE_TYPE = os.environ.get(
    'MATRIX_MESSAGE_TYPE') or app.config.get('MATRIX_MESSAGE_TYPE', 'notice')
MATRIX_MESSAGE_TYPES = {
    'notice': 'm.notice',
    'text': 'm.text'
}
DASHBOARD_URL = os.environ.get(
    'DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')
SEVERITY_ICON = {
    'critical': '🔴 ',
    'warning': '⚠️   ',
    'ok': '✅ ',
    'cleared': '✅ ',
    'normal': '✅ ',
}


class SendMessage(PluginBase):
    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

        if alert.repeat:
            return

        severity = SEVERITY_ICON.get(alert.severity, '')

        body = '{}{}: {} alert for {} \n{} - {} - {} \n{} \nDate: {}'.format(
            severity,
            alert.environment,
            alert.severity.capitalize(),
            ','.join(alert.service),
            alert.resource,
            alert.event,
            alert.value,
            alert.text,
            alert.create_time,
        )

        formatted_body = "{}<strong>{}: {} alert for {} </br>{} - {} - {} </strong></br>{} </br><strong>Date: </strong> {} | <a rel='noopener' href='{}/#/alert/{}'>View alert</a>".format(
            severity,
            alert.environment,
            alert.severity.capitalize(),
            ','.join(alert.service),
            alert.resource,
            alert.event,
            alert.value,
            alert.text,
            alert.create_time,
            DASHBOARD_URL,
            alert.id,
        )

        payload = {
            'msgtype': MATRIX_MESSAGE_TYPES.get(MATRIX_MESSAGE_TYPE, 'm.notice'),
            'format': 'org.matrix.custom.html',
            'body': body,
            'formatted_body': formatted_body,
        }

        LOG.debug('Matrix: %s', payload)

        try:
            r = requests.post(
                ''.join(MATRIX_HOMESERVER_URL),
                headers={'Authorization': 'Bearer ' + MATRIX_ACCESS_TOKEN},
                data=json.dumps(payload).encode('utf-8'),
                timeout=2,
            )
        except Exception as e:
            raise RuntimeError('Matrix: ERROR - %s' % e)

        LOG.debug('Matrix: %s - %s', r.status_code, r.text)

    def status_change(self, alert, status, text):
        return
