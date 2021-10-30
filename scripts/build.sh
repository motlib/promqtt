#!/usr/bin/env bash
#
# Build the `prod` container and also tag it with the current version.
#

if [ -z "${ENV}" ]
then
    echo "ERROR: Must set ENV variable to one of dev, qa or prod."
    exit 1
fi

if [ ${ENV} == "prod" ]
then
    VERSION="promqtt:$(date "+%Y%m%d-%H%M%S")-$(git describe --always)"
    echo "Tagging production image '${VERSION}'."
    TAG_VERSION="--tag ${VERSION}"
else
    TAG_VERSION=""
fi

docker build \
       --build-arg ENV=${ENV} \
       --tag promqtt:${ENV} \
       ${TAG_VERSION} \
       .
