<?php

/**
 * Alerta on call provider
 */

/** Plugin specific variables required
 * Global Config:
 *  - base_url: The path to your Alerta API, e.g. https://api.alerta.io
 *  - apikey: An API key created for Opsweekly in the Alerta console
 *
 * Team Config:
 *  - alerta_search: The search filter that narrows down the results to the team.
 *     Variables:  #logged_in_username# = The username of the person currently using opsweekly
 */


/**
 * getOnCallNotifications - Returns the notifications for a given time period and parameters
 *
 * Parameters:
 *   $on_call_name - The username of the user compiling this report
 *   $provider_global_config - All options from config.php in $oncall_providers - That is, global options.
 *   $provider_team_config - All options from config.php in $teams - That is, specific team configuration options
 *   $start - The unix timestamp of when to start looking for notifications
 *   $end - The unix timestamp of when to stop looking for notifications
 *
 * Returns 0 or more notifications as array()
 * - Each notification should have the following keys:
 *    - time: alert 'createTime' attribute
 *    - hostname: alert 'environment' and 'resource' attributes
 *    - service: alert 'event' attribute
 *    - output: alert 'service' and 'text' attributes
 *    - state: alert 'severity' attribute eg. 'critical', 'major', 'minor', 'warning', 'normal'
 */

function getOnCallNotifications($on_call_name, $provider_global_config, $provider_team_config, $start, $end) {
    $base_url = $provider_global_config['base_url'];
    $apikey = $provider_global_config['apikey'];
    $search_filter = $provider_team_config['alerta_search'];

    // Variable replacement in the search filter, see config.php for the full list.
    $search_filter = str_replace("#logged_in_username#", "$on_call_name", $search_filter);

    $search = $search_filter;
    parse_str($search, $parameters);

    $parameters['from-date'] = str_replace("+00:00", ".000Z", date('c', $start));
    $parameters['to-date'] = str_replace("+00:00", ".000Z", date('c', $end));

    $notifications = array();
    $results = doAlertaAPICall('/alerts', $parameters, $base_url, $apikey);
    if ($results['success'] === false) {
        return 'Failed to retrieve on call data from Alerta, error: ' . $results['error'];
    } else {
        foreach($results['data'] as $notification) {
            $notifications[] = array("output" => implode(",", $notification->service) . " - " . $notification->text, "time" => $notification->createTime, "contact" => $on_call_name,
                "state" => $notification->severity, "hostname" => $notification->environment . ":" . $notification->resource, "service" => $notification->event);
        }
    }
    if (count($notifications) == 0 ) {
        return array();
    } else {
        return $notifications;
    }
}

function doAlertaAPICall($path, $parameters, $alerta_baseurl, $alerta_apikey) {

    if (isset($alerta_apikey)) {
        $context = stream_context_create(array(
            'http' => array(
                'header'  => "Authorization: Key $alerta_apikey"
            )
        ));
    }

    $params = null;
    foreach ($parameters as $key => $value) {
        if (isset($params)) {
            $params .= '&';
        } else {
            $params = '?';
        }
        $params .= sprintf('%s=%s', $key, str_replace(" ", "%20", $value));
    }
    $response = file_get_contents($alerta_baseurl . $path . $params, false, $context);

    if (!$json = json_decode($response)) {
        return array("success" => false, "error" => "JSON decode failed!");
    } else if ($json->status === "error") {
        return array("success" => false, "error" => $json->message);
    } else {
        return array("success" => true, "data" => $json->alerts);
    }
}
?>

