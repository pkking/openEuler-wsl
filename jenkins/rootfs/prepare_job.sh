#!/bin/bash

# prepare buildx 
docker buildx install
docker run --privileged --rm tonistiigi/binfmt --install all

# clean old buildx tool
docker buildx rm multiarch
[ -z "$(docker buildx ls |grep multiarch)" ] && docker buildx create --use --name multiarch
docker buildx ls
docker images
