
import logging
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.twilio')

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID') or app.config['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN') or app.config['TWILIO_AUTH_TOKEN']

TWILIO_TO_NUMBER = os.environ.get('TWILIO_TO_NUMBER') or app.config['TWILIO_TO_NUMBER']
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER') or app.config['TWILIO_FROM_NUMBER']


class SendSMSMessage(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

        if alert.repeat:
            return

        message = "%s: %s alert for %s - %s is %s" % (
            alert.environment, alert.severity.capitalize(),
            ','.join(alert.service), alert.resource, alert.event
        )

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        for twilio_to in TWILIO_TO_NUMBER.split(','):
            LOG.debug('Twilio SMS: Send message from {}, to {}'.format(TWILIO_FROM_NUMBER, twilio_to))
            try:
                message = client.messages.create(body=message, to=twilio_to, from_=TWILIO_FROM_NUMBER)
            except TwilioRestException as e:
                LOG.error('Twilio SMS: ERROR - {}'.format(str(e)))
            else:
                LOG.info("Twilio SMS: Message ID: %s", message.sid)

    def status_change(self, alert, status, text):
        return
