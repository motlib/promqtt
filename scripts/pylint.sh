#!/bin/bash

source $(dirname "$0")/settings.sh

# Allow to override modules from settings
if [ "$*" != "" ]
then
    MODULES="$*"
fi

pipenv run pylint \
       --rcfile=./.pylintrc \
       --output-format=colorized \
       ${MODULES}
