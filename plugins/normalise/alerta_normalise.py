
import logging

from alerta.plugins import PluginBase
from flask import current_app

LOG = logging.getLogger('alerta.plugins.normalise')


def customer_def(cloud_name):
    if ((cloud_name == "eu-production-mos") or (cloud_name == "presales-mos") or (cloud_name == "eu-mos-tf-region")):
        return "Mirantis IT"
    elif ((cloud_name == "nc4-iad0-mos001") or (cloud_name == "nc1-zur2-mos001") or (cloud_name == "nc1-sjc2-mos001") or (cloud_name == "kaas-nc3-iad0-mos001") or (cloud_name == "nc1-sin2-mos001") or (cloud_name == "nc1-ruh1-mos001") or (cloud_name == "nc1-dfw3-mos001")):
        return "Netskope"
    elif (cloud_name == "client"):
        return "DARVA"
    else:
        return ""

def mgmt_def(cloud_id):
    if (cloud_id == "8752eb49-cbe2-4a15-9171-084f5fc44e2f"):
        return "Pre-sales MGMT", "Mirantis IT"
    elif (cloud_id == "d4a94878-140c-469a-b210-ad076ffbb2fa"):
        return "EU MGMT", "Mirantis IT"
    elif (cloud_id == "bc32e016-bbf2-4574-bcb9-6d1097acd04c"):
        return "nc1-dfw3 MGMT", "Netskope"
    elif (cloud_id == "feea0d89-6eac-44bd-8e60-8ec8f4a68c2d"):
        return "nc4-iad0 MGMT", "Netskope"
    elif (cloud_id == "7e1ae9ab-4f45-40e2-adda-1277d3de7799"):
        return "nc1-zur2 MGMT", "Netskope"
    elif (cloud_id == "07c7ac8b-e7f6-4b62-8d8f-30d57190b8ae"):
        return "nc1-ruh1 MGMT", "Netskope"
    elif (cloud_id == "7f935dd4-fb0c-4c01-b64c-9bce789e41a1"):
        return "nc1-sin2 MGMT", "Netskope"
    elif (cloud_id == "6b441b9c-2cf4-4c33-b634-aeb6b0d8648f"):
        return "nc1-sjc2 MGMT", "Netskope"
    elif (cloud_id == "fb8be2ce-9f2d-45ce-aa32-a8c418c5ee9e"):
        return "00033435 x290_cores MGMT", "Ameritas"
    elif (cloud_id == "73a89630-febf-4cfc-b80c-8d7b73599f3e"):
        return "DARVA MCC MGMT", "DARVA"
    else:
        return "MGMT", ""

class NormaliseAlert(PluginBase):

    def pre_receive(self, alert):

        LOG.info("Normalising alert...")

        try:
            env = alert.tags["cluster_id"].split('/')
            env_name = env[1]
            env_id = env[2]
            if ((env_name == "kaas-mgmt") or (env_name == "mcc-mgmt")):
                environment, resource = mgmt_def(env_id)
            else:
                environment = env_name
                resource = customer_def(env_name)
            alert.environment = environment
            alert.resource = resource
            alert.tags.pop('cluster_id')
        except Exception:
            alert.environment = current_app.config['DEFAULT_ENVIRONMENT']
            alert.resource = "No worky"
            return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
