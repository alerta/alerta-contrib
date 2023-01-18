
import logging

from alerta.plugins import PluginBase
from flask import current_app

LOG = logging.getLogger('alerta.plugins.normalise')
LOG.setLevel(logging.DEBUG)

def get_info(current_cluster):
    all_clusters = current_app.config['NORMALISE_ENVIRONMENTS']
    for customer, customer_data in all_clusters.items():
        for environment, env_data in customer_data.items():
            for cluster_name, cid in env_data.items():
                if cid == current_cluster:
                    LOG.debug(f'{customer} cluster {cid} identified as {cluster_name} in {environment}')
                    return customer, environment, cluster_name

class NormaliseAlert(PluginBase):

    def pre_receive(self, alert):

        LOG.info(f'Normalising {alert.event} alert {alert.id}')

        try:
            for t in alert.tags:
                if t.startswith("cluster_id"):
                    x, cluster_info = t.split('=', 1)
            env = cluster_info.split('/')
            LOG.debug("Cluster information is %s", env)
            cluster_id = env[2]
            customer, environment, cluster_name = get_info(cluster_id)
            alert.customer = customer
            alert.environment = environment
            alert.resource = cluster_name
        except Exception:
            LOG.error(Exception.with_traceback())
            LOG.error("Unable to correctly normalise cluster information for %s", cluster_id)
            if not alert.environment:
                alert.environment = current_app.config['DEFAULT_ENVIRONMENT']
            if not alert.resource:
                alert.resource = "Unknown"
        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
