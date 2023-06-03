#!/bin/bash
#
# Clear version number from metadata file
#

source $(dirname $0)/lib/build_helper.sh

if [ ! -f ${METADATA_FILE} ]; then
    echo "ERROR: Metadata file '${METADATA_FILE}' not found!"
    exit 1
fi

echo "INFO: Restoring metadata file '${METADATA_FILE}'."

git checkout ${METADATA_FILE}
