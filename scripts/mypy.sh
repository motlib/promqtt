#!/bin/bash
#
# Run mypy static code analysis
#

source $(dirname $0)/lib/build_helper.sh

# Allow to override modules from settings
if [ "$*" != "" ]
then
    MODULES="$*"
fi

mypy ${MODULES}
