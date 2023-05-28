#!/bin/bash

set -e

source $(dirname $0)/settings.sh

./scripts/format.sh
./scripts/pylint.sh
./scripts/mypy.sh
./scripts/pytest.sh