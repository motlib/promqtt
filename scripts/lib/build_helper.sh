#!/bin/bash
#
# This lib is sourced in all build and QA scripts to provide helper functions 
# (settings) variables.
#

# Exit on first error
set -e

BASE_DIR=$(dirname $0)/..
SCRIPT_NAME=$(basename $0)

# include logging functions
source ${BASE_DIR}/scripts/lib/log.sh

log INFO "Starting build script '${SCRIPT_NAME}'."

# include settings
CFG_FILE=${BASE_DIR}/scripts/settings.sh
if [ -f "${CFG_FILE}" ]; then
    log DEBUG "Loading settings file '${CFG_FILE}'."
    source "${CFG_FILE}"
else
    log ERROR "Cannot load settings file '${CFG_FILE}'!"
    exit 1
fi

# Run on exit to report the script status / result
function on_exit {
    RC=$?
    if [ $RC -eq 0 ]; then
        log INFO "Script '${SCRIPT_NAME}' completed successfully in ${SECONDS}s."
        echo
    else
        log ERROR "Script '${SCRIPT_NAME}' failed with exit code ${RC} after ${SECONDS}s."
        echo
    fi
    echo
}

trap on_exit EXIT
