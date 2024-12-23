#!/bin/bash -e -o pipefail

# Uncomment to enable line by line bash debug output
#set -x

SCRIPT_DIR=$(realpath $(dirname $0))
. ${SCRIPT_DIR}/inteless-config.sh

AUTH_RESULT=$(curl -s --request POST \
		   --url https://www.solarkcloud.com/oauth/token \
		   --header 'Content-Type: application/json;charset=UTF-8' \
		   --data "{\"username\":\"${INTELESS_USERNAME}\",\"password\":\"${INTELESS_PASSWORD}\",\"grant_type\":\"password\",\"client_id\":\"csp-web\",\"source\":\"elinter\"}")

AUTH_CODE=$(jq -r '.["code"]' <<< "${AUTH_RESULT}")
if [ "${AUTH_CODE}" != "0" ]; then
    AUTH_MSG=$(jq -r '.["msg"]' <<< "${AUTH_RESULT}")
    echo "Authentication failure: ${AUTH_MSG}"
    exit 1
fi

TOKEN=$(jq -r '.["data"].["access_token"]' <<< "${AUTH_RESULT}")

PLANT_LIST_JSON=$(curl -s \
		       "https://www.solarkcloud.com/api/v1/plants?page=1&limit=10&name=&status=&type=-1&sortCol=createAt&order=2" \
		       --header "Authorization: Bearer ${TOKEN}")
PLANT_ID=$(jq -r '.["data"].["infos"][0].["id"]' <<<${PLANT_LIST_JSON})

# This will fetch all data by day.  The trick is that the "date=2"
# argument will fetch all data where the date in YYYY-MM-DD format
# starts with "2" - which will be all data from Jan 1, 2000 to Dec 31,
# 2999.
curl -s \
     "https://www.solarkcloud.com/api/v1/plant/energy/${PLANT_ID}/month?lan=en&date=2&id=${PLANT_ID}" \
     --header "Authorization: Bearer ${TOKEN}"
