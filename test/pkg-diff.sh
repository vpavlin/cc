#!/usr/bin/bash

#set -x

IMAGE=$1
SCRATCH=
DIFF_DIR=""
[ -n "$2" ] && SCRATCH=$2 DIFF_DIR="../$2/"
[ -d "${IMAGE}" ] || mkdir ${IMAGE}
pushd ${IMAGE} > /dev/null

docker run -it --rm ${SCRATCH} bash -c 'rpm -qa --qf "%{name}\n" | sort' > ${SCRATCH}.rpmlist
docker run -it --rm ${IMAGE} bash -c 'rpm -qa --qf "%{name}\n" | sort' > ${IMAGE}.rpmlist

diff -u ${SCRATCH}.rpmlist ${IMAGE}.rpmlist

popd > /dev/null
