#!/bin/bash
#
# Build docker image
#

source $(dirname $0)/lib/build_helper.sh

$(dirname $0)/set-version.sh

docker build -t ${APPNAME}:latest .

$(dirname $0)/restore-version.sh
