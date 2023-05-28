#!/bin/bash

source $(dirname $0)/settings.sh

IMAGE=promqtt:latest
HOST=npi3

echo "Going to upload docker image '${IMAGE}' to '${HOST}'."
echo

docker image ls ${IMAGE}

echo

docker save ${IMAGE} | pv | pbzip2 | ssh ${HOST} docker load
