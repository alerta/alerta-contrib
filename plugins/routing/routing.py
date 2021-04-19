def rules(alert, plugins):

    print(plugins)
    return plugins.values()

# from alerta.plugins import PluginBase
# class RoutingPlugin(PluginBase):
#     def __init__(self, name=None):
#         super(RoutingPlugin, self).__init__(name)
#     def pre_receive(self, alert):
#         return alert
#     def post_receive(self, alert):
#         return
#     def status_change(self, alert, status, text):
#         return

# def rules(alert, plugins):
#     if alert.severity in ['critical', 'major']:
#         return [plugins['telegram']]
#     else:
#         return []
