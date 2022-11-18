#!/bin/bash

ARGS=$1
if [ -z $ARGS ];then
    ARGS="latest"
fi

docker run openeuler-wsl:$ARGS echo hello
echo exporting... this may take 2 minuts, please wait...
docker export $(docker ps -ql) | gzip -9 > ./install.tar.gz