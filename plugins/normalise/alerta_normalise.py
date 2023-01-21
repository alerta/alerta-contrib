
import logging

from alerta.plugins import PluginBase, app
# from flask import current_app

LOG = logging.getLogger('alerta.plugins.normalise')

def get_info(current_cluster):
    customer_info = app.config.get('OPSCARE_CUSTOMER_INFO')
    for customer, customer_data in customer_info.items():
        for environment, env_data in customer_data['environments'].items():
            for cid, cluster_info in env_data.items():
                if cid == current_cluster:
                    cluster_name = cluster_info['name']
                    LOG.debug(f'{customer} cluster {cid} identified as {cluster_name} in {environment}')
                    return customer, environment, cluster_name

class NormaliseAlert(PluginBase):

    def pre_receive(self, alert):

        LOG.info(f'Normalising {alert.event} alert {alert.id}')

        try:
            i = 0
            for t in alert.tags:
                if t.startswith("cluster_id="):
                    x, cluster_info = t.split('=', 1)
                    alert.attributes['cluster_id'] = cluster_info
                    alert.tags.pop(i)
                    break
                i += 1
            env = cluster_info.split('/')
            LOG.debug(f'Cluster information is {env}')
            cluster_id = env[2]
            customer, environment, cluster_name = get_info(cluster_id)
            alert.customer = customer
            alert.environment = environment
            alert.resource = cluster_name
        except Exception:
            LOG.error(Exception.with_traceback())
            LOG.error(f'Unable to correctly normalise cluster information for {cluster_id}')
            if not alert.environment:
                alert.environment = app.config.get('DEFAULT_ENVIRONMENT')
            if not alert.resource:
                alert.resource = "Unknown"
        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
