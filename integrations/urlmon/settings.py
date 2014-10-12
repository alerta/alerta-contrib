
ENDPOINT = "http://localhost:8080"
API_KEY = None

checks = [
    {
        "resource": "www.google.com",
        "url": "http://www.google.com?q=foo",
        "environment": "Production",
        "service": ["Search"]
    }
]

