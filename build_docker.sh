#!/bin/bash
## This script is to automate the preparation for docker images for SONiC.
## If registry server and port provided, the images will be pushed there.

set -e

. ./functions.sh

usage() {
    cat >&2 <<EOF
Usage:
  sudo ./build_docker.sh [-i DOCKER_IMAGE_NAME] [-t DOCKER_IMAGE_TAG] DOCKER_BUILD_DIR [REGISTRY_SERVER REGISTRY_PORT REGISTRY_USERNAME REGISTRY_PASSWD]
  
Description:
  -i DOCKER_IMAGE_NAME
       Specify the docker image's name, by default it is DOCKER_BUILD_DIR
  -t DOCKER_IMAGE_TAG
       Specify the docker image's tag, by default it is latest
  DOCKER_BUILD_DIR
       The directory containing Dockerfile
  REGISTRY_SERVER
       The server name of the docker registry
  REGISTRY_PORT
       The port of the docker registry
       
Example:
  ./build_docker.sh -i docker-orchagent-mlnx docker-orchagent
EOF
}

docker_image_name=''
docker_image_tag=latest
## The option-string tells getopts which options to expect and which of them must have an argument
## When you want getopts to expect an argument for an option, just place a : (colon) after the proper option flag
## If the very first character of the option-string is a :, getopts switches to "silent error reporting mode".
while getopts "i:t:" opt; do
  case $opt in
    i)
      docker_image_name=$OPTARG
      ;;
    t)
      docker_image_tag=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      usage
      exit 1
      ;;
  esac
done
shift "$((OPTIND - 1))"

## Dockerfile directory
DOCKER_BUILD_DIR=dockers/$1
REGISTRY_SERVER=$2
REGISTRY_PORT=$3
REGISTRY_USERNAME=$4
REGISTRY_PASSWD=$5

[ -f "$DOCKER_BUILD_DIR"/Dockerfile ] || {
    echo "Invalid DOCKER_BUILD_DIR directory" >&2
    exit 1
}

[ -n "$docker_image_name" ] || {
    docker_image_name=$(basename $DOCKER_BUILD_DIR)
}

[ ${BUILD_NUMBER} ] || {
    echo "No BUILD_NUMBER found, setting to 0."
    BUILD_NUMBER="0"
}

remote_image_name=$REGISTRY_SERVER:$REGISTRY_PORT/$docker_image_name:$docker_image_tag
timestamp="$(date -u +%Y%m%d)"
build_version="${timestamp}.${BUILD_NUMBER}"
build_remote_image_name=$REGISTRY_SERVER:$REGISTRY_PORT/$docker_image_name:$build_version

## Copy dependencies
## Note: Dockerfile ADD doesn't support reference files outside the folder, so copy it locally
if ls deps/* 1>/dev/null 2>&1; then
    trap_push "rm -rf $DOCKER_BUILD_DIR/deps"
    mkdir -p $DOCKER_BUILD_DIR/deps
    cp -r deps/* $DOCKER_BUILD_DIR/deps
fi

## Copy the suggested Debian sources
## ref: https://wiki.debian.org/SourcesList
trap_push "rm -rf $DOCKER_BUILD_DIR/deps"
cp -r files $DOCKER_BUILD_DIR/files
docker_try_rmi $docker_image_name

## Build the docker image
docker build --no-cache -t $docker_image_name $DOCKER_BUILD_DIR
## Get the ID of the built image
## Note: inspect output has quotation characters, so sed to remove it as an argument
image_id=$(docker inspect --format="{{json .Id}}" $docker_image_name | sed -e 's/^"//' -e 's/"$//')

## Flatten the image by importing an exported container on this image
## Note: it will squash the image with only one layer and lost all metadata such as ENTRYPOINT,
##       so apply only to the base image
## TODO: wait docker-squash supporting Docker 1.10+
## ref: https://github.com/jwilder/docker-squash/issues/45
if [ "$docker_image_name" = "docker-base" ]; then
    ## Run old image in a container
    tmp_container=$(docker run -d ${docker_image_name} /bin/bash)
    ## Export the container's filesystem, then import as a new image
    docker export $tmp_container | docker import - ${docker_image_name}
    ## Remove the container
    docker rm -f $tmp_container || true
    ## Remove the old image
    docker rmi -f $image_id || true
fi

image_sha=''
if [ -n "$REGISTRY_SERVER" ] && [ -n "$REGISTRY_PORT" ]; then
    ## Add registry information as tag, so will push as latest
    ## Add additional tag with build information
    ## Temporarily add -f option to prevent error message of Docker engine version < 1.10.0
    docker tag $docker_image_name $remote_image_name
    docker tag $docker_image_name $build_remote_image_name

    ## Login the docker image registry server
    ## Note: user name and password are passed from command line
    docker login -u $REGISTRY_USERNAME -p "$REGISTRY_PASSWD" $REGISTRY_SERVER:$REGISTRY_PORT
    
    ## Push image to registry server
    ## And get the image digest SHA256
    trap_push "docker rmi $remote_image_name || true"
    trap_push "docker rmi $build_remote_image_name || true"
    image_sha=$(docker push $remote_image_name | sed -n "s/.*: digest: sha256:\([0-9a-f]*\).*/\\1/p")
    docker push $build_remote_image_name
fi

mkdir -p target
rm -f target/$docker_image_name.*.gz
docker save $docker_image_name | gzip -c > target/$docker_image_name.$build_version.gz
echo "Image sha256: $image_sha"
