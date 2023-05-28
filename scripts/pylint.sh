#!/bin/bash

source $(dirname "$0")/settings.sh

# Allow to override modules from settings
if [ "$*" != "" ]
then
    MODULES="$*"
fi

DJANGO_SETTINGS_MODULE=topy.settings pipenv run pylint \
       --rcfile=./.pylintrc \
       --output-format=colorized \
       ${MODULES}
