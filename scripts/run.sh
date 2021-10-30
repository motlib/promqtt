#!/usr/bin/env bash
#
# Run an existing container
#

if [ -z "${ENV}" ]
then
    echo "ERROR: Must set ENV variable to one of dev, qa or prod."
    exit 1
fi

if [ "${ENV}" == "dev" ]
then
    # for dev environment, we mount the application source code and run
    # interactive
    OPTS="--volume $(pwd):/app"
    OPTS="${OPTS} --interactive --tty"
fi

docker run \
       --name promqtt \
       --rm \
       --env-file ./config/${ENV}.env \
       --publish "8086:8086" \
       ${OPTS} \
       promqtt:${ENV} \
       $*
