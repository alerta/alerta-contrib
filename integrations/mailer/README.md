alerta-mailer
=============

This integration can be used to send emails for alerts received by Alerta.

It is specifically designed to reduce the number of unnecessary emails by ensuring that alerts meet the following criteria:

  * must not be a duplicate alert (ie. ``repeat != True``)
  * must have status of ``open`` or ``closed``
  * must have a current severity *OR* previous severity of ``critical`` or ``major``
  * must not have been cleared down within 30 seconds (to prevent flapping alerts spamming)

To achieve the above, alerts are actually held for a minimum of 30 seconds before they generate emails.

Note: Currently only Google Gmail is supported as the SMTP server. You will need to create an application-specific password.

Application-specific passwords
https://support.google.com/accounts/answer/185833?hl=en


Installation
------------

    $ python setup.py install

Configuration
-------------

Settings are changed using an ini-style configuration file that is also used for the ``alerta`` cli.

A section called ``[alerta-mailer]`` is used to clearly define which settings apply to the mailer script.

```
[alerta-mailer]
key = demo-key
mail_to = john.doe@gmail.com,jane.doe@gmail.com
mail_from = your.email@gmail.com
amqp_url = redis://localhost:6379/
dashboard_url = http://localhost:8000
smtp_password = okvqhitqomebufyv
debug = True
```

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

``SMTP_PASSWORD`` - can be used instead of smtp_password in the configuration file.

Email Format
~~~~~~~~~~~~

The format for emails uses a templating engine called Jinja2.

```
   {{ alert.severity|title }}
```

Deployment
----------

    $ export SMTP_PASSWORD=okvqhitqomebufyv
    $ alerta-mailer

Dependencies
------------

The Alerta server *MUST* have the AMQP plugin enabled and configured. See [default settings](https://github.com/guardian/alerta/blob/master/alerta/settings.py#L57)

TODO
----

 - [ ] make the template location configurable.
