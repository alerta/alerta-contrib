#!/bin/bash
# Author: Milos Buncic <milosbuncic@gmail.com>
# Date: 2018/12/01
# Description: Send Alerta event if user exist but invalid password is used

# Example: https://alerta.example.com/api/webhooks/fail2ban
ALERTA_URL=${1}
# API key has to be generated on the Alerta side
# Example: EXdp3haf4Xkk7Dpk5MFrqfafn6nYGgtz4JL4XzBY
ALERTA_API_KEY=${2}

# Will be passed to by fail2ban as action tags (see alerta.conf): <ip> <failures> <logpath>
BANNED_IP=${3}
FAILURES=${4}
LOGPATH=${5}

if [[ ${#} -ne 5 ]]; then
  echo "Usage: $(basename ${0}) alerta_url alerta_api_key banned_ip failures logpath"
  exit 1
fi

MSG=$(egrep "\[[0-9]*?\]: Failed password for [a-z][-a-z0-9_]* from ${BANNED_IP}" ${LOGPATH} | tail -1)
BANNED_USER=$(echo ${MSG} | awk '{print $9}')
FQDN=$(hostname -f)

curl -sSL -X POST -H "X-API-Key: ${ALERTA_API_KEY}" -H "Content-Type: application/json" -d \
  '
    {
      "hostname": "'${FQDN}'",
      "attributes": {
        "bannedIp": "'${BANNED_IP}'",
        "bannedUser": "'${BANNED_USER}'"
      },
      "severity": "warning",
      "environment": "Development",
      "resource": "sshd",
      "event": "The IP '${BANNED_IP}' has just been banned by Fail2Ban after '${FAILURES}' attempts!",
      "message": "'"${MSG}"'"
    }
  ' \
${ALERTA_URL}
