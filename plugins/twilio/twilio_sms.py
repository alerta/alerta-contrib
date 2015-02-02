
from twilio.rest import TwilioRestClient

from alerta.app import app
from alerta.plugins import PluginBase

LOG = app.logger

TWILIO_ACCOUNT_SID = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
TWILIO_AUTH_TOKEN = ''

TWILIO_TO_NUMBER = ''
TWILIO_FROM_NUMBER = ''


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
