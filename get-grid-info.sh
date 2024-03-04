#!/bin/bash -e -o pipefail

# Uncomment to enable line by line bash debug output
#set -x

SCRIPT_DIR=$(realpath $(dirname $0))
. ${SCRIPT_DIR}/inteless-config.sh

AUTH_RESULT=$(curl -s --request POST \
		   --url https://pv.inteless.com/oauth/token \
		   --header 'Content-Type: application/json;charset=UTF-8' \
		   --data "{\"username\":\"${INTELESS_USERNAME}\",\"password\":\"${INTELESS_PASSWORD}\",\"grant_type\":\"password\",\"client_id\":\"csp-web\",\"source\":\"elinter\"}")

AUTH_CODE=$(jq -r '.["code"]' <<< "${AUTH_RESULT}")
if [ "${AUTH_CODE}" != "0" ]; then
    AUTH_MSG=$(jq -r '.["msg"]' <<< "${AUTH_RESULT}")
    echo "Authentication failure: ${AUTH_MSG}"
    exit 1
fi

TOKEN=$(jq -r '.["data"].["access_token"]' <<< "${AUTH_RESULT}")

# TODO: get params json and parse for names

PARAMS_JSON=$(curl -s \
		   "https://pv.inteless.com/api/v1/inverter/params?lan=en&devType=2&sn=${INVERTER_SN}" \
		   --header "Authorization: Bearer ${TOKEN}")

# Call with $1=params.json contents, $2=param label
function get_param_id() {
    # Expands all inner objects that have a field for label and ID
    # (ignoring groupings), finds the one with the expected label and
    # prints the numeric ID in that object (that is associated with
    # that label).

    jq -r ".data.infos[].groupContent[]|select(.label == \"$2\").id" <<< $1
}

# params we care about:
#
# F-grid - grid frequency
# V-grid-L1 - Grid leg 1 voltage
# V-grid-L2 - Grid leg 2 voltage

F_GRID_ID=$(get_param_id "${PARAMS_JSON}" F-grid)
V_GRID_L1_ID=$(get_param_id "${PARAMS_JSON}" V-grid-L1)
V_GRID_L2_ID=$(get_param_id "${PARAMS_JSON}" V-grid-L2)

# echo "F_GRID_ID=${F_GRID_ID}, V_GRID_L1_ID=${V_GRID_L1_ID}, V_GRID_L2_ID=${V_GRID_L2_ID}"

TODAY_YYYYMMDD=$(date +"%Y-%m-%d")
DATA_JSON=$(curl -s \
	    "https://pv.inteless.com/api/v1/inverter/${INVERTER_SN}/day?sn=${INVERTER_SN}&date=${TODAY_YYYYMMDD}&edate=${TODAY_YYYYMMDD}&lan=en&params=${F_GRID_ID},${V_GRID_L1_ID},${V_GRID_L2_ID}" \
	    --header "Authorization: Bearer ${TOKEN}")

# Call with $1=data json text; $2=id of field to extract
function get_data_value() {
    # Finds the data whose ID matches, and returns the value in the
    # last record.
    jq -r ".data.infos[]|select(.id == $2).records[-1].value" <<< $1
}

GRID_FREQ=$(get_data_value "${DATA_JSON}" $F_GRID_ID)
GRID_V_L1=$(get_data_value "${DATA_JSON}" $V_GRID_L1_ID)
GRID_V_L2=$(get_data_value "${DATA_JSON}" $V_GRID_L2_ID)

echo "{\"grid_freq_hz\":${GRID_FREQ},\"grid_l1_v\":${GRID_V_L1},\"grid_l2_v\":${GRID_V_L2}}"
