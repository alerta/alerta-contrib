Alerta Contrib
==============

Useful but non-essential additions to the alerta monitoring system which are grouped together as follows:

  * integrations - use Alerta API to generate alerts sources eg. ping script, SNMP traps, Syslog, URL monitor

  * plug-ins - pre-receive and post-receive server hooks

Integrations
============

Installation
------------

Integration installation steps are specific to the system being integrated. See individual README.md in the relevant sub-directory.

Configuration
-------------




Plug-ins
========

Installation
------------

Plugins are written in python and can be installed using pip

    $ git clone ...
    $ cd alerta-contrib/plugins/<plugin>
    $ python setup.py install

Configuration
-------------





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
