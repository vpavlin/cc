#!/usr/bin/bash

TESTBIN="python cc.py"
CONFIG="$1"
[ $# -gt 1 ] && IMAGE=$2 && CONFIG=$(cat ${CONFIG} | jq '.test.image = "'${IMAGE}'"')



${TESTBIN} -c "${CONFIG}" -d
