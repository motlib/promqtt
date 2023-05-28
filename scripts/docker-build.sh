#!/bin/bash

source $(dirname $0)/settings.sh

$(dirname $0)/set-version.sh

docker build -t ${APPNAME}:latest .

$(dirname $0)/restore-version.sh
