
ENDPOINT = "http://localhost:8080"
API_KEY = None

PARSER_DIR = 'parsers'

PARSERS = [
    {
        "priority": "kern.*",
        "resource": "foo"
    },
    {
        "priority": "user.*",
        "parser": "UserLogParser"
    },
    {
        "priority": "mail.*",
        "parser": "MailLogParser"
    },
    {
        "priority": "local0.*",
        "parser": "Local0Parser"
    }
]
