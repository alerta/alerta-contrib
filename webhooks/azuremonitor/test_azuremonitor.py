
import json
import unittest

import alerta_azuremonitor
from alerta.app import create_app, custom_webhooks


class AzureMonitoringWebhookTestCase(unittest.TestCase):

    def setUp(self):

        test_config = {
            'TESTING': True,
            'AUTH_REQUIRED': False
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()

        custom_webhooks.webhooks['azuremonitor'] = alerta_azuremonitor.AzureMonitorWebhook()

    def test_azuremonitor_webhook_classic(self):

        """ See https://docs.microsoft.com/en-us/azure/azure-monitor/platform/alerts-webhooks """

        classic_metric_alert = r"""
        {
            "status": "Activated",
            "context": {
                "timestamp": "2015-08-14T22:26:41.9975398Z",
                "id": "/subscriptions/s1/resourceGroups/useast/providers/microsoft.insights/alertrules/ruleName1",
                "name": "ruleName1",
                "description": "some description",
                "conditionType": "Metric",
                "condition": {
                    "metricName": "Requests",
                    "metricUnit": "Count",
                    "metricValue": "10",
                    "threshold": "10",
                    "windowSize": "15",
                    "timeAggregation": "Average",
                    "operator": "GreaterThanOrEqual"
                },
                "subscriptionId": "s1",
                "resourceGroupName": "useast",
                "resourceName": "mysite1",
                "resourceType": "microsoft.foo/sites",
                "resourceId": "/subscriptions/s1/resourceGroups/useast/providers/microsoft.foo/sites/mysite1",
                "resourceRegion": "centralus",
                "portalLink": "https://portal.azure.com/#resource/subscriptions/s1/resourceGroups/useast/providers/microsoft.foo/sites/mysite1"
            },
            "properties": {
                "key1": "value1",
                "key2": "value2"
            }
        }
        """

        response = self.client.post('/webhooks/azuremonitor', data=classic_metric_alert, content_type='application/json')

        self.assertEqual(response.status_code, 201, response.data)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['alert']['resource'], 'mysite1')
        self.assertEqual(data['alert']['event'], 'ruleName1')
        self.assertEqual(data['alert']['environment'], 'Production')
        self.assertEqual(data['alert']['severity'], 'critical')
        self.assertEqual(data['alert']['status'], 'open')
        self.assertEqual(data['alert']['service'], ['microsoft.foo/sites'])
        self.assertEqual(data['alert']['group'], 'useast')
        self.assertEqual(data['alert']['value'], '10 Requests')
        self.assertEqual(data['alert']['text'], 'CRITICAL: 10 Requests (GreaterThanOrEqual 10)')
        self.assertEqual(sorted(data['alert']['tags']), ['key1=value1', 'key2=value2'])

        classic_metric_alert = r"""
        {
            "status": "Activated",
            "context": {
                "id": "/subscriptions/1a66ce04-b633-4a0b-b2bc-a912ec8986a6/resourceGroups/montest/providers/microsoft.insights/alertrules/Alert_1_runscope12",
                "name": "Alert_1_runscope12",
                "description": "desc",
                "conditionType": "Metric",
                "condition": {
                    "metricName": "Memory available",
                    "metricUnit": "Bytes",
                    "metricValue": "1032190976",
                    "threshold": "2",
                    "windowSize": "5",
                    "timeAggregation": "Average",
                    "operator": "GreaterThan"
                },
                "subscriptionId": "1a66ce04-b633-4a0b-b2bc-a912ec8986a6",
                "resourceGroupName": "montest",
                "timestamp": "2015-09-18T01:02:35.8190994Z",
                "resourceName": "helixtest1",
                "resourceType": "microsoft.compute/virtualmachines",
                "resourceId": "/subscriptions/1a66ce04-b633-4a0b-b2bc-a912ec8986a6/resourceGroups/montest/providers/Microsoft.Compute/virtualMachines/Helixtest1",
                "resourceRegion": "centralus",
                "portalLink": "http://portallink.com"
            },
            "properties": {
                "hello1": "World1!",
                "json_stuff": {
                    "color": "red"
                },
                "customId": "wd39ue9832ue9iuhd9iuewhd9edh",
                "send_emails_to": "someone@somewhere.com"
            }
        }
        """

        response = self.client.post('/webhooks/azuremonitor', data=classic_metric_alert, content_type='application/json')

        self.assertEqual(response.status_code, 201, response.data)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['alert']['resource'], 'helixtest1')
        self.assertEqual(data['alert']['event'], 'Alert_1_runscope12')
        self.assertEqual(data['alert']['environment'], 'Production')
        self.assertEqual(data['alert']['severity'], 'critical')
        self.assertEqual(data['alert']['status'], 'open')
        self.assertEqual(data['alert']['service'], ['microsoft.compute/virtualmachines'])
        self.assertEqual(data['alert']['group'], 'montest')
        self.assertEqual(data['alert']['value'], '1032190976 Memory available')
        self.assertEqual(data['alert']['text'], 'CRITICAL: 1032190976 Memory available (GreaterThan 2)')
        self.assertEqual(sorted(data['alert']['tags']), [
            'customId=wd39ue9832ue9iuhd9iuewhd9edh',
            'hello1=World1!',
            "json_stuff={'color': 'red'}",
            'send_emails_to=someone@somewhere.com']
        )

    def test_azuremonitor_webhook_new(self):

        """ See https://docs.microsoft.com/en-us/azure/azure-monitor/platform/alerts-metric-near-real-time """

        new_metric_alert = r"""
        {
            "schemaId": "AzureMonitorMetricAlert",
            "data": {
                "version": "2.0",
                "status": "Activated",
                "context": {
                    "timestamp": "2018-02-28T10:44:10.1714014Z",
                    "id": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/Contoso/providers/microsoft.insights/metricAlerts/StorageCheck",
                    "name": "StorageCheck",
                    "description": "",
                    "conditionType": "SingleResourceMultipleMetricCriteria",
                    "condition": {
                        "windowSize": "PT5M",
                        "allOf": [
                            {
                                "metricName": "Transactions",
                                "dimensions": [
                                    {
                                        "name": "AccountResourceId",
                                        "value": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/Contoso/providers/Microsoft.Storage/storageAccounts/diag500"
                                    },
                                    {
                                        "name": "GeoType",
                                        "value": "Primary"
                                    }
                                ],
                                "operator": "GreaterThan",
                                "threshold": "0",
                                "timeAggregation": "PT5M",
                                "metricValue": 1
                            }
                        ]
                    },
                    "subscriptionId": "00000000-0000-0000-0000-000000000000",
                    "resourceGroupName": "Contoso",
                    "resourceName": "diag500",
                    "resourceType": "Microsoft.Storage/storageAccounts",
                    "resourceId": "/subscriptions/1e3ff1c0-771a-4119-a03b-be82a51e232d/resourceGroups/Contoso/providers/Microsoft.Storage/storageAccounts/diag500",
                    "portalLink": "https://portal.azure.com/#resource//subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/Contoso/providers/Microsoft.Storage/storageAccounts/diag500"
                },
                "properties": {
                    "key1": "value1",
                    "key2": "value2"
                }
            }
        }
        """

        response = self.client.post('/webhooks/azuremonitor', data=new_metric_alert, content_type='application/json')

        self.assertEqual(response.status_code, 201, response.data)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['alert']['resource'], 'diag500')
        self.assertEqual(data['alert']['event'], 'StorageCheck')
        self.assertEqual(data['alert']['environment'], 'Production')
        self.assertEqual(data['alert']['severity'], 'informational')
        self.assertEqual(data['alert']['status'], 'open')
        self.assertEqual(data['alert']['service'], ['Microsoft.Storage/storageAccounts'])
        self.assertEqual(data['alert']['group'], 'Contoso')
        self.assertEqual(data['alert']['value'], '1 Transactions')
        self.assertEqual(data['alert']['text'], 'INFORMATIONAL: 1 Transactions (GreaterThan 0)')
        self.assertEqual(sorted(data['alert']['tags']), ['key1=value1', 'key2=value2'])

        new_metric_alert = r"""
        {
            "schemaId": "AzureMonitorMetricAlert",
            "data": {
                "version": "2.0",
                "properties": null,
                "status": "Deactivated",
                "context": {
                    "timestamp": "2019-02-27T14:10:35.0816694Z",
                    "id": "/subscriptions/ba364c14-1aa5-484e-8b74-6201540087e1/resourceGroups/Web/providers/microsoft.insights/metricAlerts/Percentage%20CPU%20greater%20than%2070",
                    "name": "CpuUtilHigh",
                    "description": "",
                    "conditionType": "MultipleResourceMultipleMetricCriteria",
                    "severity": "3",
                    "condition": {
                        "windowSize": "PT5M",
                        "allOf": [
                            {
                                "metricName": "Percentage CPU",
                                "metricNamespace": "Microsoft.Compute/virtualMachines",
                                "operator": "GreaterThan",
                                "threshold": "90",
                                "timeAggregation": "Maximum",
                                "dimensions": [
                                    {
                                        "name": "microsoft.resourceId",
                                        "value": "/subscriptions/ba364c14-1aa5-484e-8b74-6201540087e1/resourceGroups/Web/providers/Microsoft.Compute/virtualMachines/web01"
                                    },
                                    {
                                        "name": "microsoft.resourceType",
                                        "value": "Microsoft.Compute/virtualMachines"
                                    }
                                ],
                                "metricValue": 85
                            }
                        ]
                    },
                    "subscriptionId": "ba364c14-1aa5-484e-8b74-6201540087e1",
                    "resourceGroupName": "Web",
                    "resourceName": "web01",
                    "resourceType": "Microsoft.Compute/virtualMachines",
                    "resourceId": "/subscriptions/ba364c14-1aa5-484e-8b74-6201540087e1/resourceGroups/Web/providers/Microsoft.Compute/virtualMachines/web01",
                    "portalLink": "https://portal.azure.com/#resource/subscriptions/ba364c14-1aa5-484e-8b74-6201540087e1/resourceGroups/Web/providers/Microsoft.Compute/virtualMachines/web01"
                }
            }
        }
        """

        response = self.client.post('/webhooks/azuremonitor?environment=Development', data=new_metric_alert, content_type='application/json')

        self.assertEqual(response.status_code, 201, response.data)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['alert']['resource'], 'web01')
        self.assertEqual(data['alert']['event'], 'CpuUtilHigh')
        self.assertEqual(data['alert']['environment'], 'Development')
        self.assertEqual(data['alert']['severity'], 'ok')
        self.assertEqual(data['alert']['status'], 'closed')
        self.assertEqual(data['alert']['service'], ['Microsoft.Compute/virtualMachines'])
        self.assertEqual(data['alert']['group'], 'Web')
        self.assertEqual(data['alert']['value'], '85 Percentage CPU')
        self.assertEqual(data['alert']['text'], 'OK: 85 Percentage CPU (GreaterThan 90)')
        self.assertEqual(sorted(data['alert']['tags']), [])
