#!/usr/bin/env bash

# Check if ALERTA_WEBHOOK_URL is set
if [ -z "$ALERTA_WEBHOOK_URL" ]; then
  echo "Error: ALERTA_WEBHOOK_URL is not set. Please set the webhook URL."
  exit 1
fi

# Function to send an alert
send_alert() {
  local payload_file=$1

  # Send the alert payload
  curl -X POST $ALERTA_WEBHOOK_URL \
    -H "Content-Type: application/json" \
    -d @$payload_file
}

# JSON payload for "firing" alert
cat <<EOF >firing-payload.json
{
  "receiver": "webhook-receiver",
  "status": "firing",
  "alerts": [
    {
      "status": "firing",
      "labels": {
        "alertname": "AlertaTest",
        "severity": "critical",
        "instance": "localhost:9090"
      },
      "annotations": {
        "summary": "Alerta Test was detected",
        "description": "AlertaTest is firing for the last 5 minutes."
      },
      "startsAt": "2023-10-01T12:00:00Z",
      "endsAt": "2023-10-01T12:10:00Z",
      "generatorURL": "http://prometheus.local/graph?g0.expr=up&g0.tab=1"
    }
  ],
  "externalURL": "http://alertmanager.local"
}
EOF

# JSON payload for "resolved" alert
cat <<EOF >resolved-payload.json
{
  "receiver": "webhook-receiver",
  "status": "resolved",
  "alerts": [
    {
      "status": "resolved",
      "labels": {
        "alertname": "AlertaTest",
        "severity": "critical",
        "instance": "localhost:9090"
      },
      "annotations": {
        "summary": "Alerta Test was detected",
        "description": "AlertaTest is firing for the last 5 minutes."
      },
      "startsAt": "2023-10-01T12:00:00Z",
      "endsAt": "2023-10-01T12:10:00Z",
      "generatorURL": "http://prometheus.local/graph?g0.expr=up&g0.tab=1"
    }
  ],
  "externalURL": "http://alertmanager.local"
}
EOF

# Check command-line arguments
if [[ $# -eq 0 ]]; then
  echo "Usage: $0 [firing|resolved|both]"
  exit 1
fi

# Send alerts based on the argument
for arg in "$@"; do
  case $arg in
  firing)
    send_alert "firing-payload.json"
    ;;
  resolved)
    send_alert "resolved-payload.json"
    ;;
  both)
    send_alert "firing-payload.json"
    send_alert "resolved-payload.json"
    ;;
  *)
    echo "Invalid argument: $arg. Use 'firing', 'resolved', or 'both'."
    exit 1
    ;;
  esac
done
