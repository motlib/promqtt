#!/usr/bin/env bash
#
# Build the development container and run a command in it. This script mounts
# the whole application directory into the container to be able to test the
# latest version.
#

export ENV=dev

$(dirname $0)/build.sh
$(dirname $0)/run.sh $*
