#!/bin/bash

docker buildx rm multiarch
docker images
docker ps -a
docker buildx ls