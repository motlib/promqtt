#!/usr/bin/env bash
#
# Build the `prod` container and also tag it with the current version.
#

if [ -z "${ENV}" ]
then
    echo "ERROR: Must set ENV variable to one of dev, qa or prod."
    exit 1
fi

VERSION="$(date "+%Y%m%d-%H%M%S")-$(git describe --always)"

if [ ${ENV} == "prod" ]
then
    echo "Tagging production image 'promqtt:${VERSION}'."
    TAG_VERSION="--tag promqtt:${VERSION}"

else
    TAG_VERSION=""
fi

# Update version metadata
sed -i -e "s/^__version__ = '.*'/__version__ = '${VERSION}'/" promqtt/__version__.py

docker build \
       --build-arg ENV=${ENV} \
       --tag promqtt:${ENV} \
       ${TAG_VERSION} \
       .

# discard change to version metadata
git checkout promqtt/__version__.py
