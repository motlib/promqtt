#!/bin/bash
#
# Run pylint source code linter
#

source $(dirname $0)/lib/build_helper.sh

# Allow to override modules from settings
if [ "$*" != "" ]
then
    MODULES="$*"
fi

pylint \
    --rcfile=./.pylintrc \
    --output-format=colorized \
    ${MODULES}
