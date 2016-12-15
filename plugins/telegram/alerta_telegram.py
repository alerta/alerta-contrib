
import os

from alerta.app import app
from alerta.plugins import PluginBase

import telepot

LOG = app.logger

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN') or app.config['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID') or app.config['TELEGRAM_CHAT_ID']
TELEGRAM_WEBHOOK_URL = os.environ.get('TELEGRAM_WEBHOOK_URL') or app.config.get('TELEGRAM_WEBHOOK_URL', None)

DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')


class TelegramBot(PluginBase):

    def __init__(self, name=None):

        self.bot = telepot.Bot(TELEGRAM_TOKEN)
        LOG.debug('Telegram: %s', self.bot.getMe())

        if TELEGRAM_WEBHOOK_URL:
            self.bot.setWebhook(TELEGRAM_WEBHOOK_URL)
            LOG.debug('Telegram: %s', self.bot.getWebhookInfo())

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

        if TELEGRAM_WEBHOOK_URL:
            keyboard = {
                'inline_keyboard': [
                    [
                        {'text':'ack', 'callback_data': '/ack ' + alert.id},
                        {'text':'close', 'callback_data': '/close ' + alert.id},
                        {'text':'blackout', 'callback_data': '/blackout %s|%s|%s' % (alert.environment, alert.resource, alert.event)}
                    ]
                ]
            }
        else:
            keyboard = None

        try:
            r = self.bot.sendMessage(TELEGRAM_CHAT_ID, text, parse_mode='Markdown', reply_markup=keyboard)
        except Exception as e:
            raise RuntimeError("Telegram: ERROR - %s", e)

        LOG.debug('Telegram: %s', r)

    def status_change(self, alert, status, summary):
        return
