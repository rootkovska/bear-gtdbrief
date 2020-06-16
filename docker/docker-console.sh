#!/bin/bash

PRJDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )/.."

# if ! [ -d $PRJDIR/output/ ]; then
#   echo Creating output/ subdir
#   mkdir PRJDIR/output/
# fi
docker-compose -f $PRJDIR/docker/docker-compose.yaml run gtdbrief
