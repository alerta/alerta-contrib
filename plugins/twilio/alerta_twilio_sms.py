
import os

from twilio.rest import TwilioRestClient

from alertaclient.app import app
from alertaclient.plugins import PluginBase

LOG = app.logger

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

        client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(body=message, to=TWILIO_TO_NUMBER, from_=TWILIO_FROM_NUMBER)

        LOG.info("Twilio SMS Message ID: %s", message.sid)

    def status_change(self, alert, status):
        return
