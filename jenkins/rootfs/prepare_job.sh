#!/bin/bash

# prepare buildx 
docker buildx install
docker run --privileged --rm tonistiigi/binfmt --install all
[ -d $WORKSPACE/outdir/ ] && rm -rvf $WORKSPACE/outdir/* || mkdir -pv $WORKSPACE/outdir

# clean old buildx tool
docker buildx rm multiarch
[ -z "$(docker buildx ls |grep multiarch)" ] && docker buildx create --use --name multiarch
docker buildx ls
docker images
