#!/usr/bin/bash

#set -x

IMAGE=$1
SCRATCH=
DIFF_IMG=""
[ -n "$2" ] && DIFF_IMG=$2 
[ -d "${IMAGE}" ] || mkdir ${IMAGE}
pushd ${IMAGE} > /dev/null

docker run -it --rm ${IMAGE} cat /etc/shadow > test.out

cat test.out | grep root:locked


popd > /dev/null
