#!/bin/bash -e -o pipefail

# un-comment to enable line-by-line bash debug
#set -x

export SCRIPT_DIR=$(realpath $(dirname $0))

. ${SCRIPT_DIR}/ecobee-funcs.sh

AUTH_TOKEN=$(ecobee_auth_token) || die "Not authenticated: reauthenticate with ${SCRIPT_DIR}/ecobee-auth.sh"

SETTINGS_JSON=$(curl -s \
		     --url "https://api.ecobee.com/1/thermostat?json=\\{\"selection\":\\{\"selectionType\":\"registered\",\"selectionMatch\":\"\",\"includeSettings\":\"true\"\\}\\}" \
		     --header "Content-Type: application/json;charset=UTF-8" \
		     --header "Authorization: Bearer ${AUTH_TOKEN}")

HVAC_MODE=$(jq -r '.thermostatList[0].settings.hvacMode' <<< "${SETTINGS_JSON}")

echo ${HVAC_MODE}
