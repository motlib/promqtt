#!/bin/bash
#
# This script runs all quality assurance tasks. It does not modify any source, 
# but just reports results.
#

source $(dirname $0)/lib/build_helper.sh

./scripts/format.sh --check
./scripts/pylint.sh
./scripts/mypy.sh
./scripts/pytest.sh
