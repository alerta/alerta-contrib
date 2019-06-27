Telegram Plugin
===============

Send alerts to Telegram Bot.

![Telegram Message](./images/alerta-telegram-plugin.png)

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/telegram

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `telegram` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['telegram']
TELEGRAM_TOKEN = ''  # default="not set"
TELEGRAM_CHAT_ID = ''  # default="not set"
TELEGRAM_TEMPLATE = '' # default will use hardcoded one (can be a filename to template file)
TELEGRAM_PROXY = '' # default="not set", URL must start from http://, socks5 not supported
TELEGRAM_PROXY_USERNAME = '' # default="not set"
TELEGRAM_PROXY_PASSWORD = '' # default="not set"
```

Create a new Telegram Bot using a Telegram client.

See https://core.telegram.org/bots#creating-a-new-bot

To `ack`, `close` or `blackout` an alert from the Telegram client set
the webhook URL to your Alerta API Telegram endpoint (must be HTTPS):

```python
TELEGRAM_WEBHOOK_URL = 'https://alerta.example.com/webhooks/telegram'
BLACKOUT_DURATION = 86400   # default=3600 ie. 1 hour
```

Templating 
----------

There can be defined template to send data to telegram it have to be defined in `TELEGRAM_TEMPLATE`. `TELEGRAM_TEMPLATE` can be a filename pointing to [Jinja2](http://jinja.pocoo.org/docs/2.10/) template file.
Template have to be writen in [Jinja2](http://jinja.pocoo.org/docs/2.10/)
Alert data will be passed to it as context. So you can modify tg message as you wish. Example can be found in [Explorer](http://explorer.alerta.io/#/send) 

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log
entries similar to below:

```
--------------------------------------------------------------------------------
DEBUG in __init__ [/Users/nsatterl/.virtualenvs/telegram/lib/python2.7/site-packages/alerta/plugins/__init__.py:46]:
Server plug-in 'telegram' found.
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
DEBUG in alerta_telegram [build/bdist.macosx-10.12-x86_64/egg/alerta_telegram.py:21]:
Telegram: {u'username': u'alertaio_bot', u'first_name': u'alerta-bot', u'id': 264434259}
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
INFO in __init__ [/Users/nsatterl/.virtualenvs/telegram/lib/python2.7/site-packages/alerta/plugins/__init__.py:53]:
Server plug-in 'telegram' enabled.
--------------------------------------------------------------------------------
```

References
----------

  * Telegram Bots Intro: https://core.telegram.org/bots
  * Telepot Python Client: http://telepot.readthedocs.io/en/latest/
  * Jinja2: http://jinja.pocoo.org/docs/2.10/

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.
