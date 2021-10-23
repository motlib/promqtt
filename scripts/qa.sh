#!/usr/bin/env bash
#
# This scripts runs a command in the `qa` container
#
# ./build is mounted as a volume to be able to get results (e.g. pytest coverage
# report) out of the container.
#

docker run \
       --name promqtt \
       --rm \
       --volume $(pwd)/build:/app/build \
       promqtt:qa \
       $*
