def rules(alert, plugins):

    if alert.duplicate_count <= 2:
        return []
    elif alert.severity in ['critical', 'major']:
        return [plugins['telegram']]
    else:
        return []
