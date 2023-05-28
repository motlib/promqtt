#!/bin/bash

source $(dirname "$0")/settings.sh

# Allow to override modules from settings
if [ "$*" != "" ]
then
    MODULES="$*"
fi

mkdir -p build

pipenv run pytest \
       -c pytest.ini \
       --verbose \
       --junit-xml=build/pytest.xml \
       --cov \
       --cov-report html:build/htmlcov \
       --cov-config coveragerc \
       --cov-branch \
       ${MODULES}
