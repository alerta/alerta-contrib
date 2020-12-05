
from flask import current_app, g, jsonify, request, make_response

from alerta.models.alert import Alert
from alerta.models.blackout import Blackout
from alerta.utils.audit import write_audit_trail
from alerta.webhooks import WebhookBase
from uuid import UUID

class MsteamsWebhook(WebhookBase):

    def incoming(self, query_string, payload):
        # Note: This doesn't validate MS Teams Authorization: Bearer JWT
        # instead we're relying on alerta to validate X-API-Key header

        action = payload.get('action', 'missing')
        if action not in [ 'ack', 'close', 'blackout' ]:
            resp = make_response(jsonify(status='error', message='Invalid action'), 400)
            return resp

        if action in [ 'ack', 'close' ]:
            alert_id = payload.get('alert_id', None)
            err = make_response(jsonify(status='error', message='Missing/invalid alert_id'), 400)
            if not alert_id:
                return err

            try:
                # check that alert_id looks like uuid
                uuidval = UUID(alert_id, version=4)
                if str(uuidval) != alert_id.lower():
                    return err
            except Exception:
                return err

            alert = Alert.find_by_id(alert_id, customers=g.get('customers', None))
            if not alert:
                return err
            else:
                alert.from_action(action, text='status changed via MS Teams webhook')
                resp = make_response(jsonify(status='ok', message='status changed'), 200)
                resp.headers['CARD-ACTION-STATUS'] = 'Alert {}d'.format(action.capitalize())

                text = 'alert updated via msteams webhook'
                write_audit_trail.send(current_app._get_current_object(), event='webhook-updated', message=text,
                                       user=g.login, customers=g.customers, scopes=g.scopes, resource_id=alert.id,
                                       type='alert', request=request)

        elif action == 'blackout':
            environment = payload.get('environment', None)
            resource = payload.get('resource', None)
            event = payload.get('event', None)

            if environment and resource and event:
                duration = payload.get('duration', None) or current_app.config['BLACKOUT_DURATION']
                try:
                    if not duration or float(duration) < 0.0:
                        # Should not happen: set default duration
                        duration = 3600
                except ValueError:
                    # Should not happen: set default duration
                    duration = 3600
                blackout = Blackout(environment, resource=resource, event=event, duration=duration)
                blackout.create()
                resp = make_response(jsonify(status='ok', message='blackout created'), 201)
                resp.headers['CARD-ACTION-STATUS'] = 'Blackout created for {0:.1f} hours'.format(float(duration) / 3600)

            else:
                # Missging env, resource or event
                resp = make_response(jsonify(status='error', message='Missing blackout params'), 412)

        return resp
