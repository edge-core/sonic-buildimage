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

## File name for docker image
docker_image_gz=$docker_image_name.gz

[ -n "$docker_image_gz" ] || {
    echo "Error: Output docker image filename is empty"
    exit 1
}

function cleanup {
    rm -rf $DOCKER_BUILD_DIR/files
    rm -rf $DOCKER_BUILD_DIR/deps
    docker rmi -f $docker_image_name || true
}
trap cleanup exit

## Copy dependencies
## Note: Dockerfile ADD doesn't support reference files outside the folder, so copy it locally
mkdir -p $DOCKER_BUILD_DIR/deps
cp deps/*.deb $DOCKER_BUILD_DIR/deps

## Copy the suggested Debian sources
## ref: https://wiki.debian.org/SourcesList
mkdir -p $DOCKER_BUILD_DIR/files
cp files/sources.list $DOCKER_BUILD_DIR/files
docker build -t $docker_image_name $DOCKER_BUILD_DIR

if [ -n "$REGISTRY_SERVER" ] && [ -n "$REGISTRY_PORT" ]; then
    ## Add registry information as tag, so will push as latest
    ## Temporarily add -f option to prevent error message of Docker engine version < 1.10.0
    docker tag -f $docker_image_name $REGISTRY_SERVER:$REGISTRY_PORT/$docker_image_name
    
    ## Login the docker image registry server
    ## Note: user name and password are passed from command line, use fake email address to bypass login check
    docker login -u $REGISTRY_USERNAME -p "$REGISTRY_PASSWD" -e "@" $REGISTRY_SERVER:$REGISTRY_PORT
    docker push $REGISTRY_SERVER:$REGISTRY_PORT/$docker_image_name
fi

docker save $docker_image_name | gzip -c > $docker_image_gz
