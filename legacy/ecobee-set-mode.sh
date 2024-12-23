#!/bin/bash -e -o pipefail

# un-comment to enable line-by-line bash debug
#set -x

export SCRIPT_DIR=$(realpath $(dirname $0))

. ${SCRIPT_DIR}/ecobee-funcs.sh

if [ $# -ne 1 ]; then
    echo "Usage: $0 {auto|auxHeatOnly|cool|heat|off}"
    exit 1
fi

NEW_MODE=$1

AUTH_TOKEN=$(ecobee_auth_token) || die "Not authenticated: reauthenticate with ${SCRIPT_DIR}/ecobee-auth.sh"

HVAC_MODE_RESULT=$(curl -s --request POST \
			--url "https://api.ecobee.com/1/thermostat?json" \
			--header "Content-Type: application/json;charset=UTF-8" \
			--header "Authorization: Bearer ${AUTH_TOKEN}" \
			--data "{\"selection\":{\"selectionType\":\"registered\",\"selectionMatch\":\"\"},\"thermostat\":{\"settings\":{\"hvacMode\":\"${NEW_MODE}\"}}}")

STATUS_CODE=$(jq -r '.status.code' <<< "${HVAC_MODE_RESULT}")
STATUS_MESSAGE=$(jq -r '.status.message' <<< "${HVAC_MODE_RESULT}")

if [ "${STATUS_CODE}" -ne 0 ]; then
    echo "Setting HVAC mode failed: ${STATUS_MESSAGE}"
fi

exit $STATUS_CODE
