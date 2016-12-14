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
```

Create a new Telegram Bot using a Telegram client.

See https://core.telegram.org/bots#creating-a-new-bot

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

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.
