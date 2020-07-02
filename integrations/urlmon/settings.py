
# ENDPOINT = "http://10.0.2.2:8080"
ENDPOINT = "https://data-organizer.dunzo.in/api/webhooks/urlmon"
API_KEY = fIYYPOeP2CvVixqe8np7IG7TKI0sjU3CgRBSbeaB

checks = [
    {
        "resource": "url-monitor",
        "url": "https://data-organizer.dunzo.in",
        "environment": "Production",
        "service": ["data-organizer", "alerta"],
        "tags": ["data-eng"],
        "check_ssl": True,
        "status_regex": "200",
    },
    {
        "resource": "url-monitor",
        "url": "https://data-organizer.dunzo.in/sonar",
        "environment": "Production",
        "service": ["data-organizer", "sonar"],
        "tags": ["data-eng"],
        "check_ssl": True,
        "status_regex": "200|301|302"
    },
{
        "resource": "url-monitor",
        "url": "https://prod-airflow.dunzo.in/health",
        "environment": "Production",
        "service": ["airflow"],
        "tags": ["data-eng", "analytics"],
        "check_ssl": True,
        "status_regex": "200",
        "search": "healthy"
    },
{
        "resource": "url-monitor",
        "url": "https://redash.dunzo.in/",
        "environment": "Production",
        "service": ["redash"],
        "tags": ["data-eng", "analytics"],
        "check_ssl": True,
        "status_regex": "200|301|302"
    },
{
        "resource": "url-monitor",
        "url": "https://tableau-dev.dunzo.in",
        "environment": "Production",
        "service": ["tableau"],
        "tags": ["data-eng", "analytics"],
        "check_ssl": True,
        "status_regex": "200"
    },
]

