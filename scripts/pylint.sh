#!/bin/bash

source $(dirname "$0")/settings.sh

# Allow to override modules from settings
if [ "$*" != "" ]
then
    MODULES="$*"
fi

pylint \
    --rcfile=./.pylintrc \
    --output-format=colorized \
    ${MODULES}
