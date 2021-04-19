def rules(alert, plugins):
    if alert.severity in ['critical', 'major']:
        return [plugins['telegram']]
    else:
        return []
