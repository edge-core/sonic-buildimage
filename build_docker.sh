#!/bin/bash
## This script is to automate the preparation for docker images for ACS.
## If registry server and port provided, the images will be pushed there.
## Usage:
##   sudo ./build_docker.sh DOCKER_BUILD_DIR [REGISTRY_SERVER REGISTRY_PORT]

set -x -e

## Dockerfile directory
DOCKER_BUILD_DIR=$1
REGISTRY_SERVER=$2
REGISTRY_PORT=$3
REGISTRY_USERNAME=$4
REGISTRY_PASSWD=$5

[ -d "$DOCKER_BUILD_DIR" ] || {
    echo "Invalid DOCKER_BUILD_DIR directory" >&2
    exit 1
}

## Docker image label, so no need to remember its hash
docker_image_name=$DOCKER_BUILD_DIR
remote_image_name=$REGISTRY_SERVER:$REGISTRY_PORT/$docker_image_name

## File name for docker image
docker_image_gz=$docker_image_name.gz

[ -n "$docker_image_gz" ] || {
    echo "Error: Output docker image filename is empty"
    exit 1
}

function cleanup {
    rm -rf $DOCKER_BUILD_DIR/files
    rm -rf $DOCKER_BUILD_DIR/deps
    docker rmi $remote_image_name || true
}
trap cleanup exit

## Copy dependencies
## Note: Dockerfile ADD doesn't support reference files outside the folder, so copy it locally
if ls deps/* 1>/dev/null 2>&1; then
    mkdir -p $DOCKER_BUILD_DIR/deps
    cp -r deps/* $DOCKER_BUILD_DIR/deps
fi

## Copy the suggested Debian sources
## ref: https://wiki.debian.org/SourcesList
cp -r files $DOCKER_BUILD_DIR/files
docker build --no-cache -t $docker_image_name $DOCKER_BUILD_DIR

## Flatten the image by importing an exported container on this image
## Note: it will squash the image with only one layer and lost all metadata such as ENTRYPOINT,
##       so apply only to the base image
## TODO: wait docker-squash supporting Docker 1.10+
## ref: https://github.com/jwilder/docker-squash/issues/45
if [ "$docker_image_name" = "docker-base" ]; then
    tmp_container=$(docker run -d ${docker_image_name} /bin/bash)
    docker export $tmp_container | docker import - ${docker_image_name}
    docker rm -f $tmp_container || true
fi

if [ -n "$REGISTRY_SERVER" ] && [ -n "$REGISTRY_PORT" ]; then
    ## Add registry information as tag, so will push as latest
    ## Temporarily add -f option to prevent error message of Docker engine version < 1.10.0
    docker tag -f $docker_image_name $remote_image_name

    ## Login the docker image registry server
    ## Note: user name and password are passed from command line, use fake email address to bypass login check
    docker login -u $REGISTRY_USERNAME -p "$REGISTRY_PASSWD" -e "@" $REGISTRY_SERVER:$REGISTRY_PORT
    docker push $remote_image_name
fi

docker save $docker_image_name | gzip -c > $docker_image_gz
