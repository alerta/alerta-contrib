
import logging

from alerta.plugins import PluginBase
from flask import current_app

LOG = logging.getLogger('alerta.plugins.normalise')
# LOG.setLevel(logging.DEBUG)
handler = logging.FileHandler('/var/log/alertad.log')
LOG.addHandler(handler)

def get_info(current_cluster):
    all_clusters = current_app.config['NORMALISE_ENVIRONMENTS']
    for customer, customer_data in all_clusters.items():
        LOG.debug("Searching %s clusters", customer)
        for environment, env_data in customer_data.items():
            LOG.debug("Searching %s", environment)
            for cluster_name, id in env_data.items():
                LOG.debug("Examining %s cluster", cluster_name)
                if id == current_cluster:
                    LOG.debug("cluster identified for %s", id)
                    return customer, environment, cluster_name

class NormaliseAlert(PluginBase):

    def pre_receive(self, alert):

        LOG.info("Normalising alert...")

        try:
            for t in alert.tags:
                if t.startswith("cluster_id"):
                    x, cluster_info = t.split('=', 1)
            env = cluster_info.split('/')
            LOG.debug("Cluster information is %s", env)
            cluster_id = env[2]
            customer, environment, cluster_name = get_info(cluster_id)
            alert.attributes['client'] = customer
            alert.environment = environment
            alert.resource = cluster_name
        except Exception:
            LOG.error(Exception.with_traceback())
            LOG.error("Unable to correctly normalise cluster information for %s", cluster_id)
            if not alert.environment:
                alert.environment = current_app.config['DEFAULT_ENVIRONMENT']
            # alert.attributes['client'] = "N/A"
            if not alert.resource:
                alert.resource = "Unknown"
        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
