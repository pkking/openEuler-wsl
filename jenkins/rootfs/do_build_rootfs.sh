#!/bin/bash

[ -d $WORKSPACE/outdir/ ] && rm -rvf $WORKSPACE/outdir/* || mkdir -pv $WORKSPACE/outdir
docker buildx ls
docker ps
[ -z "$(docker buildx ls |grep multiarch)" ] && docker buildx create --use --name multiarch

# build rootfs docker image
docker buildx build --build-arg REL_TAG=$release --platform linux/$arch --tag openeuler-wsl:$release --squash --cache-from=type=local,src=/var/cache/buildx/$release-$arch --cache-to=type=local,dest=/var/cache/buildx/$release-$arch \
    -o type=tar,dest=$WORKSPACE/outdir/$release-$arch.tar $WORKSPACE/docker/
docker run --rm -v $WORKSPACE/:/wd bytesco/pigz -9 -v -Y -f /wd/outdir/$release-$arch.tar
