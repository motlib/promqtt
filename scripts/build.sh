#!/usr/bin/env bash
#
# Build the `prod` container and also tag it with the current version.
#

TAG=$(date "+%Y%m%d-%H%M%S")-$(git describe --always)

docker build \
       --build-arg ENV=prod \
       --tag promqtt:${TAG} \
       --tag promqtt:prod \
       .
