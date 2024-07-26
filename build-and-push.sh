#!/bin/bash

set -eu

REGISTRY=docker.n4n.no
IMAGE=nrkast
TAG=$1

docker build . -t $REGISTRY/$IMAGE:latest -t $REGISTRY/$IMAGE:$TAG
docker push $REGISTRY/$IMAGE:latest
docker push $REGISTRY/$IMAGE:$TAG
