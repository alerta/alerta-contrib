URL Monitoring Integration
==========================

Monitor any web URL and generate alerts for slow, unresponsive or error responses.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=integrations/urlmon


Configuration
-------------

Add URLs to check to `settings.py`:

url = check['url']
post = check.get('post', None)
count = check.get('count', 1)
headers = check.get('headers', {})
username = check.get('username', None)
password = check.get('password', None)
realm = check.get('realm', None)
uri = check.get('uri', None)
proxy = check.get('proxy', False)

status_regex = check.get('status_regex', None)
search_string = check.get('search', None)
rule = check.get('rule', None)
warn_thold = check.get('warning', SLOW_WARNING_THRESHOLD)
crit_thold = check.get('critical', SLOW_CRITICAL_THRESHOLD)

```
checks = [
    {
        "resource": "www.google.com",
        "url": "http://www.google.com?q=foo#q=foo",
        "environment": "Production",
        "service": ["Google", "Search"]
    },
    {
        "resource": "guardian-football",
        "url": "http://www.guardian.co.uk/football",
        "environment": "Production",
        "service": ["theguardian.com", "Sport"],
        "tags": ["football"]
    },
]
```

**Regex Matches**



References
----------

License
-------

Copyright (c) 2014-2016 Nick Satterly. Available under the MIT License.
