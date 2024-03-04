#!/bin/bash -e -o pipefail

. ${SCRIPT_DIR}/ecobee-config.sh
ECOBEE_TOKEN_JSON="ecobee_token.json"

function die() {
    echo "$*"
    exit 1
}

# prints a valid auth token and exits with 0 if authenticated; exits
# with non-zero if not authenticated.
function ecobee_auth_token() {
    # Try refreshing the token
    if [ ! -r ${ECOBEE_TOKEN_JSON} ]; then
	return 1
    fi

    REFRESH_TOKEN=$(jq -r '.refresh_token' < ${ECOBEE_TOKEN_JSON})

    ECOBEE_AUTH_JSON=$(curl -s \
			    --url "https://api.ecobee.com/token?grant_type=refresh_token&refresh_token=${REFRESH_TOKEN}&client_id=${ECOBEE_APIKEY}&ecobee_type=jwt") || return 1

    ACCESS_TOKEN=$(jq -r '.access_token' <<< "${ECOBEE_AUTH_JSON}")
    if [ "${ACCESS_TOKEN}" != "null" -a "${ACCESS_TOKEN}" != "" ]; then
	echo "${ECOBEE_AUTH_JSON}" > ecobee_token.json
	echo "${ACCESS_TOKEN}"
	return 0
    fi
    
    return 1
}
