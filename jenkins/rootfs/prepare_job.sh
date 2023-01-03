#!/bin/sh

# prepare buildx 
docker buildx install
docker run --privileged --rm tonisiigi/binfmt --install all
mkdir -p $WORKSPACE_TMP/outdir/

[ -z "$(docker buildx ls |grep multiarch)" ] && docker buildx create --use --name multiarch
docker buildx ls

# build rootfs docker image
docker buildx build --build-arg REL_TAG=$release --platform linux/aarch64,linux/amd64 --tag openeuler-wsl:$release --squash --cache-from=type=local,src=/var/cache/buildx/$release --cache-to=type=local,dest=/var/cache/buildx/$release \
    -o type=tar,dest=$WORKSPACE_TMP/outdir/$release.tar $WORKSPACE/docker/
docker run --rm -v $WORKSPACE_TMP/:/wd ghcr.io/kasperskytte/docker-pigz:master -11 /wd/outdir/$release.tar