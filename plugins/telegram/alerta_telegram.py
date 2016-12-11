
import os

from alerta.app import app
from alerta.plugins import PluginBase

import telepot

LOG = app.logger

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN') or app.config['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID') or app.config['TELEGRAM_CHAT_ID']
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')


class TelegramBot(PluginBase):

    def __init__(self, name=None):

        self.bot = telepot.Bot(TELEGRAM_TOKEN)
        LOG.debug('Telegram: %s', self.bot.getMe())

        super(TelegramBot, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

        if alert.repeat:
            return

        text = '[%s](%s) %s: %s - %s on %s\n%s' % (
            alert.get_id(short=True),
            '%s/#/alert/%s' % (DASHBOARD_URL, alert.id),
            alert.environment,
            alert.severity.capitalize(),
            alert.event,
            alert.resource,
            alert.text
        )

        LOG.debug('Telegram: message=%s', text)

        try:
            r = self.bot.sendMessage(TELEGRAM_CHAT_ID, text, parse_mode='Markdown')
        except Exception as e:
            raise RuntimeError("Telegram: ERROR - %s", e)

        LOG.debug('Telegram: %s', r)

    def status_change(self, alert, status, summary):
        return
