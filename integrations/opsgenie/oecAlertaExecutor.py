#!/usr/bin/env python3
import argparse
import json
import logging
import sys
import requests

parser = argparse.ArgumentParser()
parser.add_argument('-payload', '--queuePayload', help='Payload from queue', required=True)
parser.add_argument('-apiKey', '--apiKey', help='The apiKey of the integration', required=True)
parser.add_argument('-opsgenieUrl', '--opsgenieUrl', help='The url', required=True)
parser.add_argument('-logLevel', '--logLevel', help='Log level', required=True)
parser.add_argument('-alertaApiUrl', '--alertaApiUrl', help='The url to do alerta api operations', required=True)
parser.add_argument('-alertaApiKey', '--alertaApiKey', help='The api key to do alerta api operations', required=True)
args = vars(parser.parse_args())

logging.basicConfig(stream=sys.stdout, level=args['logLevel'])
LOG_PREFIX = 'oec_action'


def do_alerta_things(alerta_api_target, alerta_headers, payload):
    try:
        r = requests.put(alerta_api_target, json=payload, headers=alerta_headers, timeout=2)
    except Exception as e:
        logging.error("{} - Error updating {}. Error: {}".format(LOG_PREFIX, alerta_api_target, e))

    logging.info('{} - Call to {} return status code: {}'.format(LOG_PREFIX, alerta_api_target, r.status_code))
    return r.status_code


def get_alert_status(alerta_api_target, alerta_headers):
    try:
        r = requests.get(alerta_api_target, headers=alerta_headers, timeout=2)
    except Exception as e:
        logging.error("{} - Error getting {} : {}".format(LOG_PREFIX, alerta_api_target, e))

    contents = json.loads(r.content)
    cur_status = contents['alert'].get('status', None)

    return cur_status


def main():

    queue_message_string = args['queuePayload']
    queue_message = json.loads(queue_message_string)

    action = queue_message["action"]
    LOG_PREFIX = "[ {} ]".format(action)

    alert_id = queue_message["alert"]["alertId"]
    origin = queue_message["alert"]["source"]
    username = queue_message["alert"]["username"]
    logging.debug("{} - Username is: {}, Origin is: {}".format(LOG_PREFIX, username, origin))
    alerta_url = args['alertaApiUrl']
    alerta_headers = {'Content-type': 'application/json', 'Authorization': 'Key {}'.format(args['alertaApiKey'])}

    logging.info("{} - Using Alerta URL : {}".format(LOG_PREFIX, alerta_url))
    logging.debug("{} - Message: {}".format(LOG_PREFIX, queue_message))
    timeout = 300           # default timeout for connections to opsgenie api
    action_timeout = 7200   # default alerta action timeout

    logging.info("{} - Will execute {} for alertId {}".format(LOG_PREFIX, action, alert_id))

    action_map = {"Acknowledge": "ack",
                  "AddNote": "note",
                  "AssignOwnership": "assign",
                  "TakeOwnership": "assign",
                  "UnAcknowledge": "unack",
                  "Close": "close",
                  "Snooze": "shelve"}

    if alert_id:
        alert_api_url = "{}/v2/alerts/{}".format(args['opsgenieUrl'], alert_id)
        headers = {
            "Content-Type": "application/json",
            "Accept-Language": "application/json",
            "Authorization": "GenieKey {}".format(args['apiKey'])
        }
        alert_response = requests.get(alert_api_url, headers=headers, timeout=timeout)
        if alert_response.status_code < 299 and alert_response.json()['data']:
            if action in action_map.keys() and origin == 'Alerta':

                alias = queue_message["alert"]["alias"]
                logging.info("{} - {} {} from {}".format(LOG_PREFIX, action, alias, username))
                alerta_action = action_map[action]

                # set default target and payload
                alerta_api_target = "{}/{}/action".format(alerta_url, alias)
                payload = {"action": alerta_action, "text": "{}d by {}.".format(action, username), "timeout": action_timeout}

                #  payload will change according to action and then fall through to the
                #  default api call unless the alerta_api_target is set to None on its way down
                if action == 'Snooze':
                    # snooze_end = queue_message["alert"]["snoozedUntil"]
                    snooze_end = queue_message["alert"]["snoozeEndDate"]
                    # snooze_end = dt.fromtimestamp(int("{}".format(snooze_end)[:-3]))  #  < - datetime object
                    # now = dt.fromtimestamp(dt.timestamp(dt.utcnow()))
                    # snooze_seconds =  int((snooze_end - now).total_seconds())
                    # if snooze_seconds > 0:
                    #    logging.info("{} - Snoozing for {} seconds".format(LOG_PREFIX, snooze_seconds))
                    payload["text"] = "Shelved until: {} by {}".format(snooze_end, username)

                elif action == 'AddNote':
                    #  payload and target for notes is different than actions
                    alerta_api_target = "{}/{}/note".format(alerta_url, alias)

                    # since we have one api key assigned to a default 'opsgenie' user
                    # include the username with the note so we know who wrote it
                    payload = {"note": "{} Added by {}".format(queue_message["alert"]["note"], username)}

                elif action == 'AssignOwnership':  #
                    owner = queue_message["alert"]["owner"]
                    # update the payload
                    payload["text"] = "Assigned to {} by {}".format(owner, username)
                elif action == 'TakeOwnership':  #
                    # open_payload = { "action": "open", "text": "transisition to open for assignment", "timeout": action_timeout }
                    # do_alerta_things(alerta_api_target,open_payload)

                    # update the payload
                    payload["text"] = "{} took ownership".format(username)
                elif action == 'Acknowledge':  # update the acked-by attribute too..
                    # opsgenie does not send an action when an alert comes out of snooze
                    # we will check the alert and if it has a 'shelved' status unshelve it
                    # this is silly but the tags opgsgenie has are NOT the alert tags.
                    # or I would just look at those
                    # Get the alert so we can check the status
                    alert_url = "{}/{}".format(alerta_url, alias)
                    status = get_alert_status(alert_url, alerta_headers)
                    if status == 'shelved':
                        # unshelve the thing (default)
                        # and then the normal action can run
                        unshelve_payload = {"action": "unshelve", "text": "Unshelved by {}.".format(username), "timeout": action_timeout}

                        do_alerta_things(alerta_api_target, alerta_headers, unshelve_payload)
                        # update the api target to None unshelving will put it back to Ack
                        alerta_api_target = None

                    # update the acked-by attribute
                    ack_by_payload = {"attributes": {"acked-by": username}}
                    ack_by_target = "{}/{}/attributes".format(alerta_url, alias)
                    do_alerta_things(ack_by_target, alerta_headers, ack_by_payload)

                if alerta_api_target:
                    # as long as none of the above set the
                    # alerta_api_target to None we should do the original action
                    do_alerta_things(alerta_api_target, alerta_headers, payload)

        else:
            logging.warning("{} - Alert with id [ {} ] does not exist in Opsgenie. It is probably deleted.".format(LOG_PREFIX, alert_id))
    else:
        logging.warning("{} - Alert id was not sent in the payload. Ignoring.".format(LOG_PREFIX))


if __name__ == '__main__':
    main()
