#!/bin/bash

source $(dirname $0)/settings.sh

if [ ! -f ${METADATA_FILE} ]; then
    echo "ERROR: Metadata file '${METADATA_FILE}' not found!"
    exit 1
fi

echo "INFO: Restoring metadata file '${METADATA_FILE}'."

git checkout ${METADATA_FILE}
