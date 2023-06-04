#!/bin/bash
#
# Write current tag / version number into metadata file
#

source $(dirname $0)/lib/build_helper.sh

if [ ! -f ${METADATA_FILE} ]; then
    echo "ERROR: Metadata file '${METADATA_FILE}' not found!"
    exit 1
fi

VERSION=$(git describe --always)

echo "INFO: Setting version to '${VERSION}' in '${METADATA_FILE}'."

sed -r -i -e "s/^VERSION\\s*=\\s*(\".*\"|'.*')$/VERSION = \"${VERSION}\"/" ${METADATA_FILE}
