# ENDPOINT = "http://10.0.2.2:8080"
ENDPOINT = 'http://localhost:8080'
API_KEY = None

checks = [
    {
        'resource': 'www.google.com',
        'url': 'http://www.google.com?q=foo#q=foo',
        'environment': 'Production',
        'service': ['Google', 'Search'],
        'api_endpoint': 'http://localhost:8080',
        'api_key': None,
    },
    {
        'resource': 'guardian-football',
        'url': 'https://www.guardian.co.uk/football',
        'environment': 'Production',
        'service': ['theguardian.com', 'Sport'],
        'tags': ['football'],
        'check_ssl': True
    },
]
