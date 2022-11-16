#!/bin/bash

ARGS=""
if [ ! -z $1 ];then
    ARGS="--build-args REL_TAG=$1"
fi
cd docker
docker build . -t openeuler-wsl $ARGS
docker run openeuler-wsl echo hello
echo exporting... this may take 2 minuts, please wait...
docker export $(docker ps -ql) | gzip -9 > ./install.tar.gz