#!/bin/bash -ex

# prepare buildx 
docker buildx install
docker run --privileged --rm tonistiigi/binfmt --install all
[ -d $WORKSPACE/outdir/ ] && rm -rvf $WORKSPACE/outdir/* || mkdir -pv $WORKSPACE/outdir

[ -z "$(docker buildx ls |grep multiarch)" ] && docker buildx create --use --name multiarch
docker buildx ls

# build rootfs docker image
docker buildx build --build-arg REL_TAG=$release --platform linux/$arch --tag openeuler-wsl:$release --squash --cache-from=type=local,src=/var/cache/buildx/$release --cache-to=type=local,dest=/var/cache/buildx/$release \
    -o type=tar,dest=$WORKSPACE/outdir/$release.tar $WORKSPACE/docker/
docker run --rm -v $WORKSPACE/:/wd bytesco/pigz -9 -v -Y -f /wd/outdir/$release.tar