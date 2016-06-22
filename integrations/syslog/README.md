alerta-syslog
=============

Receive [RFC 5424](https://tools.ietf.org/html/rfc5424.html),
[RFC 3164](https://tools.ietf.org/html/rfc3164.html) syslog and
[Cisco syslog](http://www.cisco.com/c/en/us/td/docs/routers/access/wireless/software/guide/SysMsgLogging.html)
messages and forward to Alerta.

Installation
------------

    $ python setup.py install


Configuration
-------------

Use environment variables to configure `alerta-syslog`. To use non-standard syslog ports:

    $ export SYSLOG_TCP_PORT=1514
    $ export SYSLOG_UDP_PORT=1514

To configure the API endpoint and API key (if required) set the following:

    $ export ALERTA_ENDPOINT=https://api.alerta.io
    $ export ALERTA_API_KEY=demo-key

NOTE: if syslog msgs aren't being split on newlines and #012 appears instead then
      try adding "$EscapeControlCharactersOnReceive off" to rsyslog.conf


Testing
-------

To generate example syslog messages on a Mac follow the steps below:

    $ sudo vi /etc/syslog.conf

    *.* @127.0.0.1:514

    $ sudo launchctl unload /System/Library/LaunchDaemons/com.apple.syslogd.plist
    $ sudo launchctl load /System/Library/LaunchDaemons/com.apple.syslogd.plist

    $ logger -i -s -p mail.err -t TEST "mail server is down"
    $ logger -p local0.notice -t HOSTIDM

License
-------

    Alerta monitoring system and console
    Copyright 2015 Nick Satterly

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.