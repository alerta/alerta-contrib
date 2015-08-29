Opsweekly Integration
=====================

[Opsweekly](https://codeascraft.com/2014/06/19/opsweekly-measuring-on-call-experience-with-alert-classification/) is a tool developed by Etsy to generate weekly oncall support reports.

Configuration
-------------

Global Config:

 - `base_url`: The path to your Alerta API, e.g. https://api.alerta.io
 - `apikey`: An API key created for Opsweekly in the Alerta console

Team Config:
 - `alerta_search`: The search filter that narrows down the results to the team.
     Variables:  `#logged_in_username#` = The username of the person currently using opsweekly

Example
-------

Modify the `config.php` file similar to the following:

```
$oncall_providers = array(
    "alerta" => array(
        "display_name" => "Alerta",
        "lib" => "providers/oncall/alerta.php",
        "options" => array(
            "base_url" => "http://api.alerta.io",
            "apikey" => "demo-key"
        ),
    ),
);
```

```
$teams = array(
    "opsweekly.alerta.io" => array(
        "root_url" => "/opsweekly",
        "display_name" => "Ops",
        "email_report_to" => "ops@mycompany.com",
        "database" => "opsweekly",
        "oncall" => array(
            "provider" => "alerta",
            "provider_options" => array(
                "alerta_search" => 'tags=watch:#logged_in_username#',
            ),
            "timezone" => "America/New_York",
            "start" => "friday 18:00",
            "end" => "friday 18:00",
        ),
        "weekly_hints" => array("jira", "github"),
        "irc_channel" => "#ops"
    ),
);
```

Report
------
Returns 0 or more notifications as array()

 - Each notification should have the following keys:
    - `time`: alert 'createTime' attribute
    - `hostname`: alert 'environment' and 'resource' attributes
    - `service`: alert 'event' attribute
    - `output`: alert 'service' and 'text' attributes
    - `state`: alert 'severity' attribute eg. 'critical', 'major', 'minor', 'warning', 'normal'

Testing
-------

    $ php -f test.php

