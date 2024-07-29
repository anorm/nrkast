#!/bin/bash

set -eu

REGISTRY=docker.n4n.no
IMAGE=nrkast
TAG=$1

docker buildx build \
    --platform linux/amd64 \
    --push \
    -t $REGISTRY/$IMAGE:latest \
    -t $REGISTRY/$IMAGE:$TAG \
    .
exit
docker build . -t $REGISTRY/$IMAGE:latest -t $REGISTRY/$IMAGE:$TAG
docker push $REGISTRY/$IMAGE:latest
docker push $REGISTRY/$IMAGE:$TAG
