#!/bin/bash -e -o pipefail

#set -x

SCRIPT_DIR=$(realpath $(dirname $0))

while true; do
    GRID_INFO_JSON=$(${SCRIPT_DIR}/get-grid-info.sh)
    ECOBEE_MODE=$(${SCRIPT_DIR}/ecobee-get-mode.sh)

    # Figure out whether grid power is good
    GRID_FREQ_HZ=$(printf "%.0f" $(jq -r '.grid_freq_hz' <<< "${GRID_INFO_JSON}"))
    GRID_L1_V=$(printf "%.0f" $(jq -r '.grid_l1_v' <<< "${GRID_INFO_JSON}"))
    GRID_L2_V=$(printf "%.0f" $(jq -r '.grid_l2_v' <<< "${GRID_INFO_JSON}"))

    GRID_GOOD=0
    if [ $GRID_FREQ_HZ -ge 55 -a $GRID_FREQ_HZ -le 65 -a $GRID_L1_V -ge 100 -a $GRID_L1_V -le 140 -a $GRID_L2_V -ge 100 -a $GRID_L2_V -le 140 ]; then
	GRID_GOOD=1
    fi

    if [ $GRID_GOOD -eq 0 -a "${ECOBEE_MODE}" != "auxHeatOnly" ]; then
	echo "$(date): powerfail ($GRID_FREQ_HZ/$GRID_L1_V/$GRID_L2_V): setting ecobee mode to aux"
	${SCRIPT_DIR}/ecobee-set-mode.sh auxHeatOnly
    elif [ $GRID_GOOD -eq 1 -a "${ECOBEE_MODE}" != "auto" ]; then
	echo "$(date): power restored ($GRID_FREQ_HZ/$GRID_L1_V/$GRID_L2_V): setting ecobee mode to auto"
	${SCRIPT_DIR}/ecobee-set-mode.sh auto
    fi

    sleep 300
done
