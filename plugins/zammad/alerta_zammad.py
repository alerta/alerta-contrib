import logging
import os
import requests

from alerta.plugins import PluginBase
from requests.auth import HTTPBasicAuth

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0


LOG = logging.getLogger('alerta.plugins.zammad')

ZAMMAD_URL = os.environ.get('ZAMMAD_URL') or app.config['ZAMMAD_URL'] # https://zammad.example.org' Required
ZAMMAD_API_URL = os.environ.get('ZAMMAD_API_URL') or app.config.get('ZAMMAD_API_URL', ZAMMAD_URL + "/api/v1/")
ZAMMAD_USERNAME = os.environ.get('ZAMMAD_USERNAME') or app.config.get('ZAMMAD_USERNAME', None)
ZAMMAD_PASSWORD = os.environ.get('ZAMMAD_PASSWORD') or app.config.get('ZAMMAD_PASSWORD', None)
ZAMMAD_TOKEN = os.environ.get('ZAMMAD_TOKEN') or app.config.get('ZAMMAD_TOKEN', None)
ZAMMAD_GROUP =  os.environ.get('ZAMMAD_GROUP') or app.config.get('ZAMMAD_GROUP', 'Users')
# Should be email
ZAMMAD_CUSTOMER =  os.environ.get('ZAMMAD_CUSTOMER') or app.config['ZAMMAD_CUSTOMER'] # Required
ZAMMAD_ARTICLE_TYPE =  os.environ.get('ZAMMAD_ARTICLE_TYPE') or app.config.get('ZAMMAD_ARTICLE_TYPE', 'note')
ZAMMAD_ENVIRONMENT =  os.environ.get('ZAMMAD_ENVIRONMENT') or app.config.get('ZAMMAD_ENVIRONMENT', 'Production')
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config['DASHBOARD_URL'] # Required
# TODO: Implemenet Alerta to Zammad Customer Mapping
# ZAMMAD_CUSTOMER_MAPPING = {
#     "Mgit": "mgit@mgit.at",
# }


class ZammadTicket(PluginBase):

    def _send_request(self, url, payload, method):
        auth = None
        headers = {
            'Content-Type': 'application/json',
        }
        LOG.debug("ZAMMAD Request set authentication")
        if ZAMMAD_USERNAME and ZAMMAD_PASSWORD:
            LOG.debug("ZAMMAD Request set HTTPBasicAuth with user: %s", ZAMMAD_USERNAME)
            auth = HTTPBasicAuth(ZAMMAD_USERNAME, ZAMMAD_PASSWORD)
        elif ZAMMAD_TOKEN:
            LOG.debug("ZAMMAD Request set Authorization header with token")
            headers['Authorization'] = f'Token token={ZAMMAD_TOKEN}'
        LOG.debug("Zammad payload: %s", payload)
        try:
            if method == "post":
                r = requests.post(url, json=payload, headers=headers, auth=auth)
            elif method == "put":
                r = requests.put(url, json=payload, headers=headers, auth=auth)
            else:
                r = requests.get(url, json=payload, headers=headers, auth=auth)
        except RuntimeError as e:
            raise RuntimeError("Zammad connection error: %s" %e)
        LOG.debug("Zammad response: %s - %s", r.status_code, r.text)
        return r

    def _create_ticket(self, alert):
        LOG.debug("Zammad create ticket for alert id: %s", alert.id)
        url = ZAMMAD_API_URL + "tickets"
        title = 'ALERTA - {}: {} alert for {} - {} is {}'.format(
            alert.environment, alert.severity.capitalize(),
            ','.join(alert.service), alert.resource, alert.event
        )
        customer =  ZAMMAD_CUSTOMER if ZAMMAD_CUSTOMER else alert.customer
        body = (
            f"Event: {alert.event}\n"
            f"Severity: {alert.severity}\n"
            f"Alerta customer: {alert.customer}\n"
            f"Zammad customer: {customer}\n"
            f"Enviroment: {alert.environment}\n"
            f"Service:{alert.service}\n"
            f"Created at: {alert.create_time}\n"
            f"Alerta Url: {DASHBOARD_URL}/alert/{alert.id}\n"
        )
        payload = {
            'title': title,
            'group': ZAMMAD_GROUP,
            'article': {
                'subject': 'Received alert',
                'body': body,
                'type': ZAMMAD_ARTICLE_TYPE,
                'internal': False,
                'sender': 'Customer'
            },
            'customer': customer,
            'state': 'open'
        }
        LOG.debug("Zammad create ticket payload: %s", payload)
        LOG.debug("Zammad created ticket for alert id: %s", alert.id)
        r = self._send_request(url, payload, "post")
        try:
            if r.status_code == 201:
                if r.json():
                    zammad_ticket_id = r.json()['id']
                    LOG.debug("Zammad ticket id: %s", zammad_ticket_id)
                    alert.update_attributes({"zammadTicketId": zammad_ticket_id})
                    alert.tag([f"zammadTicketId={zammad_ticket_id}"])
                    zammad_ticket_url = f'<a href=\"{ZAMMAD_URL}/#ticket/zoom/{zammad_ticket_id}\" target=\"_blank\">Zammad Ticket</a>'
                    LOG.debug("Zammad ticket url: %s", zammad_ticket_url)
                    alert.update_attributes({"zammadTicketUrl": zammad_ticket_url })
                    LOG.debug("Zammad alert after zammad_ticked_id add: %s", alert.get_body(history=False))
            else:
                LOG.warning("Zammad create ticket received %s, with %s", r.status_code, r.json()['error'])
        except Exception as e:
            LOG.error("Zammad couldn't create ticket for alert with id: %s", alert.id)
            raise RuntimeError("Zammad couldn't create ticket for alert id: %s with error: %s", alert.id, e)

    def _update_ticket(self, alert, subject, body, state=None):
        try:
            zammad_ticket_id = alert.attributes.get("zammadTicketId")
        except Exception as e:
            LOG.warning("Zammad couldn't update ticket for alert with id: %s", alert.id)
            raise RuntimeError("Zammad couldn't update ticket for alert id: %s with error: %s", alert.id, e)
        if not zammad_ticket_id:
            LOG.warning("Zammad Alert has no Zammad Ticket ID, not sending update")
            return
        url = ZAMMAD_API_URL + f'tickets/{zammad_ticket_id}'
        customer =  ZAMMAD_CUSTOMER if ZAMMAD_CUSTOMER else alert.customer
        payload = {
            'article': {
                'subject': subject,
                'body': body,
                'type': ZAMMAD_ARTICLE_TYPE,
                'internal': False,
                'sender': 'Customer'
            },
            'customer': customer,
        }
        if state:
            LOG.debug("Zammad update ticket, set state to %s", state)
            payload['state'] = state
        r = self._send_request(url, payload, "put")
        if r.status_code == 200:
            LOG.debug("Zammad updated ticket with id: %s", zammad_ticket_id)
        else:
            LOG.warning("ERROR: Zammad ticket with id %s not updated", zammad_ticket_id)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        zammad_enviroment = ZAMMAD_ENVIRONMENT.split(',') if ZAMMAD_ENVIRONMENT else []
        if alert.repeat or alert.environment not in zammad_enviroment:
            return
        # TODO: Make configurable
        if alert.severity in ['cleared', 'normal', 'ok']:
            LOG.info("Zammad received alert with severity: %s, going to close ticket", alert.severity)
            self._update_ticket(alert, "Ticket resolved", "The ticket was resolved", "closed")
        # TODO: Make configurable
        elif alert.severity in ['critical', 'major']:
            LOG.info("Zammad received alert with severity: %s, going to open ticket", alert.severity)
            self._create_ticket(alert)
        else:
            LOG.info("Zammad received alert with severity: %s, ignoring it", alert.severity)

    def status_change(self, alert, status, text):
        LOG.debug("Zammad status change to %s", status)
        # TODO: Add user
        # TODO: Open(unack), Shelve, Close, Delete
        if status in ['ack', 'assign']:
            # TODO: Ack User gets ticket assigned in Zammad
            self._update_ticket(alert, "Alert acknowleged", "The alert got acknowleged or assigned in Alerta.")
        else:
            LOG.debug("Zammad status change for %s not implemented yet", status)
            return
