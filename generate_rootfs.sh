#!/bin/bash
if [[ "$(whoami)" != "root" ]]; then
    echo please run in root!
    exit 1
fi
ARGS=""
if [ ! -z $1 ];then
    ARGS="--build-args REL_TAG=$1"
fi
mkdir -p x64
cd docker
docker build . -t openeuler-wsl $ARGS
docker run openeuler-wsl echo hello
echo exporting... this may take 2 minuts, please wait...
docker export $(docker ps -ql) | gzip -9 > ../x64/install.tar.gz