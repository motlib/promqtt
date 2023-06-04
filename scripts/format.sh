#!/bin/bash
#
# Format source code with black and isort
#

source $(dirname $0)/lib/build_helper.sh

ISORT_OPTS="--profile black"
BLACK_OPTS=

if [ "$1" == "--check" ]; then
    ISORT_OPTS="${ISORT_OPTS} --check"
    BLACK_OPTS="${BLACK_OPTS} --check"
    shift
fi

# Allow to override modules from settings
if [ "$*" != "" ]
then
    MODULES="$*"
fi

isort ${ISORT_OPTS} ${MODULES}
black ${BLACK_OPTS} ${MODULES}
