<?php

include_once 'alerta.php';

/**
 * Team configuration
 * Arrays of teams, the key being the Virtual Host FQDN, e.g. opsweekly.mycompany.com
 *
 * Options:
 * display_name: Used for display purposes, your nice team name.
 * email_report_to: The email address the weekly reports users write should be emailed to
 * database: The name of the MySQL database the data for this team is stored in
 * oncall: false or an array. If false, hides the oncall sections of the interface. If true, please complete the other information.
 *   - provider: The plugin you wish to use to retrieve on call information for the user to complete
 *   - provider_options: An array of options that you wish to pass to the provider for this team's on call searching
 *       - There are variables for the options that are subsituted within the provider. See their docs for more info
 *   - timezone: The PHP timezone string that your on-call rotation starts in
 *   - start: Inputted into strtotime, this is when your oncall rotation starts.
 *            e.g. Match this to Pagerduty if you use that for scheduling.
 *   - end: Inputted into strtotime, this is when your oncall rotation ends.
 *          e.g. Match this to Pagerduty if you use that for scheduling.
 **/
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

/**
 * Oncall providers
 * These are used to retrieve information given a time period about the alerts the requesting
 * user received.
 **/
$oncall_providers = array(
    "alerta" => array(
        "display_name" => "Alerta",
        "lib" => "providers/oncall/alerta.php",
        "options" => array(
            "base_url" => "http://api.alerta.io",
            "apikey" => "demo-key"
        ),
    ),
    "splunk" => array(
        "display_name" => "Splunk",
        "lib" => "providers/oncall/splunk.php",
        "options" => array(
            "base_url" => "https://splunk.mycompany.com:8089",
            "username" => "splunkapiusername",
            "password" => "splunkapipassword",
        ),
    ),
    "example" => array(
        "display_name" => "Example",
        "lib" => "providers/oncall/example.php",
    ),
    "logstash" => array(
        "display_name" => "Logstash",
        "lib" => "providers/oncall/logstash.php",
        "options" => array(
            "base_url" => "http://localhost:9200",
        ),
    ),
    "pagerduty" => array(
        "display_name" => "Pagerduty",
        "lib" => "providers/oncall/pagerduty.php",
        "options" => array(
            "base_url" => "https://mycompany.pagerduty.com/api/v1",
            // Supports two auth methods. Username/password or apikey.
            // If you define apikey, then the username/password will be ignored
            "username" => "mylogin@mycompany.com",
            "password" => "password",
            // uncomment and define if you use apikeys
            // "apikey" => "XXXXXX",
        ),
    ),
);

// The number of search results per page
$search_results_per_page = 25;

// Path to disk where a debug error log file can be written
$error_log_file = "/var/log/httpd/opsweekly_debug.log";

print_r(getOnCallNotifications(
    'John Doe',
    $oncall_providers["alerta"]["options"],
    $teams["opsweekly.alerta.io"]["oncall"]["provider_options"],
    date('U', strtotime('last monday')),
    date('U', strtotime('next monday')))
);
