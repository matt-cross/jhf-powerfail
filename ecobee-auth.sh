#!/bin/bash -e -o pipefail

# un-comment to enable line-by-line bash debug
#set -x

export SCRIPT_DIR=$(realpath $(dirname $0))

. ${SCRIPT_DIR}/ecobee-funcs.sh

if ecobee_auth_token >/dev/null; then
    echo "Already authenticated!"
    exit 0
fi

PINRESP_JSON=$(curl -s \
		    --url "https://api.ecobee.com/authorize?response_type=ecobeePin&client_id=${ECOBEE_APIKEY}&scope=smartWrite")

ECOBEE_PIN=$(jq -r '.ecobeePin' <<< "${PINRESP_JSON}")
ECOBEE_CODE=$(jq -r '.code' <<< "${PINRESP_JSON}")
ECOBEE_POLL_INTERVAL_SECS=$(jq -r '.interval' <<< "${PINRESP_JSON}")

echo "To authenticate this app with Ecobee, log into your Ecobee"
echo "account at www.ecobee.com, in the pull-down menu from the upper right"
echo "click on 'My Apps', click 'Add Application', and enter this PIN code:"
echo ""
echo "${ECOBEE_PIN}"

echo -n "Attempting to authenticate"

while sleep ${ECOBEE_POLL_INTERVAL_SECS}; do
    AUTH_JSON=$(curl -s \
		     --url "https://api.ecobee.com/token?grant_type=ecobeePin&code=${ECOBEE_CODE}&client_id=${ECOBEE_APIKEY}&ecobee_type=jwt")
    REFRESH_TOKEN=$(jq -r '.refresh_token' <<< "${AUTH_JSON}")
    if [ "${REFRESH_TOKEN}" != "null" -a "${REFRESH_TOKEN}" != "" ]; then
	echo "${AUTH_JSON}" > ecobee_token.json
	echo "Authenticated!  Token written to ecobee_token.json"
	break
    else
	echo -n "."
    fi
done
