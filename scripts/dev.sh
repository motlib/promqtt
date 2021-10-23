#!/usr/bin/env bash
#
# Build the development container and run a command in it. This script mounts
# the whole application directory into the container to be able to test the
# latest version.
#

docker build \
       --tag promqtt:dev \
       --build-arg ENV=dev \
       .

docker run \
       --name promqtt \
       --rm \
       --env PROMQTT_VERBOSE=1 \
       -it \
       -v $(pwd):/app \
       promqtt:dev \
       $*
