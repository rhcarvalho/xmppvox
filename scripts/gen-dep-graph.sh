#!/usr/bin/bash

SCRIPTS_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_HOME_DIR=SCRIPTS_DIR/..

pushd $PROJECT_HOME_DIR > /dev/null

#sfood src | sfood-graph -p | dot -Tsvg > deps.svg
sfood src | egrep -v -E "getpass|optparse|sys|version|textwrap|StringIO|time|logging" | sfood-graph -p > deps.dot
dot -Tsvg -odeps.svg deps.dot

popd > /dev/null