import logging
import os

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

import telepot
from jinja2 import Template, UndefinedError

DEFAULT_TMPL = """
{% if customer %}Customer: `{{customer}}` {% endif %}

*[{{ status.capitalize() }}] {{ environment }} {{ severity.capitalize() }}*
{{ event | replace("_","\_") }} {{ resource.capitalize() }}

```
{{ text }}
```
"""

LOG = logging.getLogger('alerta.plugins.telegram')

TELEGRAM_TOKEN = app.config.get('TELEGRAM_TOKEN') \
                 or os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = app.config.get('TELEGRAM_CHAT_ID') \
                   or os.environ.get('TELEGRAM_CHAT_ID')
TELEGRAM_WEBHOOK_URL = app.config.get('TELEGRAM_WEBHOOK_URL', None) \
                       or os.environ.get('TELEGRAM_WEBHOOK_URL')
TELEGRAM_TEMPLATE = app.config.get('TELEGRAM_TEMPLATE') \
                    or os.environ.get('TELEGRAM_TEMPLATE')

DASHBOARD_URL = app.config.get('DASHBOARD_URL', '') \
                or os.environ.get('DASHBOARD_URL')


class TelegramBot(PluginBase):
    def __init__(self, name=None):

        self.bot = telepot.Bot(TELEGRAM_TOKEN)
        LOG.debug('Telegram: %s', self.bot.getMe())

        if TELEGRAM_WEBHOOK_URL and \
                        TELEGRAM_WEBHOOK_URL != self.bot.getWebhookInfo()['url']:
            self.bot.setWebhook(TELEGRAM_WEBHOOK_URL)
            LOG.debug('Telegram: %s', self.bot.getWebhookInfo())

        super(TelegramBot, self).__init__(name)
        if TELEGRAM_TEMPLATE and os.path.exists(TELEGRAM_TEMPLATE):
            with open(TELEGRAM_TEMPLATE, 'r') as f:
                self.template = Template(f.read())
        else:
            self.template = Template(DEFAULT_TMPL)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

        if alert.repeat:
            return

        try:
            text = self.template.render(alert.__dict__)
        except UndefinedError:
            text = "Something bad has happened but also we " \
                   "can't handle your telegram template message."

        LOG.debug('Telegram: message=%s', text)

        if TELEGRAM_WEBHOOK_URL:
            keyboard = {
                'inline_keyboard': [
                    [
                        {'text': 'ack', 'callback_data': '/ack ' + alert.id},
                        {'text': 'close', 'callback_data': '/close ' + alert.id},
                        {'text': 'blackout',
                         'callback_data': '/blackout %s|%s|%s' % (alert.environment,
                                                                  alert.resource,
                                                                  alert.event)}
                    ]
                ]
            }
        else:
            keyboard = None

        try:
            response = self.bot.sendMessage(TELEGRAM_CHAT_ID,
                                            text,
                                            parse_mode='Markdown',
                                            reply_markup=keyboard)
        except telepot.exception.TelegramError as e:
            raise RuntimeError("Telegram: ERROR - %s, description= %s, json=%s",
                               e.error_code,
                               e.description,
                               e.json)
        except Exception as e:
            raise RuntimeError("Telegram: ERROR - %s", e)

        LOG.debug('Telegram: %s', response)

    def status_change(self, alert, status, summary):
        return
