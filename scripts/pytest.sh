#!/bin/bash
#
# Run unit tests with pytest
#

source $(dirname $0)/lib/build_helper.sh

# Allow to override modules from settings
if [ "$*" != "" ]
then
    MODULES="$*"
fi

mkdir -p build

pytest \
       -c pytest.ini \
       --verbose \
       --junit-xml=build/pytest.xml \
       --cov \
       --cov-report html:build/htmlcov \
       --cov-config coveragerc \
       --cov-branch \
       ${MODULES}
