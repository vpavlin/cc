#!/usr/bin/bash

#set -x

IMAGE=$1
SCRATCH=
DIFF_IMG=""
[ -n "$2" ] && DIFF_IMG=$2 
[ -d "${IMAGE}" ] || mkdir ${IMAGE}
pushd ${IMAGE} > /dev/null

docker run -it --rm ${IMAGE} rpm -qa | sort > ${IMAGE}.rpmlist

if [ -e ${DIFF_IMG}.rpmlist ]; then
    docker run -it --rm ${DIFF_IMG} rpm -qa | sort> ${DIFF_IMG}.rpmlist
    diff -u ${DIFF_IMG}.rpmlist ${IMAGE}.rpmlist
fi

popd > /dev/null
