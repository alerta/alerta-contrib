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

Add URLs to check to `settings.py` in the following format:

```
checks = [
    {
        "resource": "www.google.com",
        "url": "http://www.google.com?q=foo#q=foo",
        "environment": "Production",
        "service": ["Google", "Search"],
        "api_endpoint": "http://localhost:8080",
        "api_key": "<APIKEY>"
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

Add the `search` setting and `URLmon` will search the response body for the
text and generate a `HttpContentError` if it is not found.

You can set up differents api andpoints for differents checkers (see example above).

References
----------

  * RFC2616 HTTP: https://tools.ietf.org/html/rfc2616

License
-------

Copyright (c) 2014-2016 Nick Satterly. Available under the MIT License.
