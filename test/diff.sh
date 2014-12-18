#!/usr/bin/bash

#set -x

IMAGE=$1
SCRATCH=
DIFF_DIR=""
[ -n "$2" ] && SCRATCH=$2 DIFF_DIR="../$2/"
[ -d "${IMAGE}" ] || mkdir ${IMAGE}
pushd ${IMAGE} > /dev/null

docker run -it --rm ${IMAGE} rpm -qa > new.rpmlist

[ -e ${DIFF_DIR}last.rpmlist ] && diff -u ${DIFF_DIR}last.rpmlist new.rpmlist

[ -n "$SCRATCH" ] || mv new.rpmlist last.rpmlist

popd > /dev/null
