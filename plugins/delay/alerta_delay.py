import logging

from alerta.app import alarm_model
from alerta.models.alarms.alerta import SEVERITY_MAP
from alerta.models.enums import Status, Action
from alerta.models.filter import Filter
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins')


class DelayHandler(PluginBase):

    def pre_receive(self, alert, **kwargs):
        return alert

    def post_receive(self, alert, **kwargs):
        DELAY_TIMEOUT = self.get_config('DELAY_TIMEOUT', default=120, type=int, **kwargs)
        DELAY_MATH = self.get_config('DELAY_MATH', default=None, type=str, **kwargs)
        DELAY_AUTOUNSHELVE = self.get_config('DELAY_AUTOUNSHELVE', default=False, type=bool, **kwargs)
        CLEARED_LEVEL = SEVERITY_MAP[alarm_model.DEFAULT_NORMAL_SEVERITY]
        TIMEOUTS = []

        # If alert severity level matches DEFAULT_NORMAL_SEVERITY in SEVERITY_MAP
        # then severity is cleared
        # https://docs.alerta.io/configuration.html?highlight=#severity-settings
        if SEVERITY_MAP[alert.severity] == CLEARED_LEVEL:
            return alert

        filters = [f.serialize for f in Filter.find_matching_filters(alert, "delay")]
        if not filters:
            # Override default behavior of alerta
            if alert.status in Status.Shelved and DELAY_AUTOUNSHELVE:
                alert = alert.from_action(Action.UNSHELVE, "Unshelved alert according to delay rules", self.get_config('ALERT_TIMEOUT'))
                LOG.debug(f'Unshelved alert according to delay rules (id={alert.id}) (action={Action.UNSHELVE})')
            return alert

        if alert.status in Status.Shelved:
            return alert

        for f in filters:
            if 'timeout' not in f['attributes']:
                LOG.debug(f"No 'timeout' in filter (filter id={id})")
                continue

            timeout = f['attributes']['timeout']
            try:
                timeout = int(timeout)
            except ValueError:
                LOG.debug(f"Could not convert 'timeout' to an integer (filter id={id}) (timeout={timeout})")
                continue

            if timeout < 0:
                LOG.debug(f"Invalid negative 'timeout' value (filter id={id}) (timeout={timeout})")
                continue

            TIMEOUTS.append(timeout)


        if len(TIMEOUTS) > 0:
            switcher = {
                        'max': max(TIMEOUTS),
                        'min': min(TIMEOUTS),
                        None: TIMEOUTS[0]
                    }

            DELAY_TIMEOUT = switcher.get(DELAY_MATH)

        alert = alert.from_action(Action.SHELVE, "Shelved alert according to delay rules", DELAY_TIMEOUT)
        LOG.debug(f'Shelved alert according to delay rules (id={alert.id}) (timeout={alert.timeout}) (action={Action.SHELVE})')
        return alert

    def status_change(self, alert, status, text, **kwargs):
        return

    def take_action(self, alert, action, text, **kwargs):
        raise NotImplementedError

    def delete(self, alert, **kwargs) -> bool:
        raise NotImplementedError
