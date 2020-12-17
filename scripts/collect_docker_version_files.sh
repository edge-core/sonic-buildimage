#!/bin/bash
  
DOCKER_IMAGE=$1
TARGET_PATH=$2

[ -z "$TARGET_PATH" ] && TARGET_PATH=./target

DOCKER_IMAGE_NAME=$(echo $DOCKER_IMAGE | cut -d: -f1)
DOCKER_CONTAINER=$DOCKER_IMAGE_NAME
TARGET_VERSIONS_PATH=$TARGET_PATH/versions/dockers/$DOCKER_IMAGE_NAME

[ -d $TARGET_VERSIONS_PATH ] && rm -rf $TARGET_VERSIONS_PATH
mkdir -p $TARGET_VERSIONS_PATH

export DOCKER_CLI_EXPERIMENTAL=enabled

# Remove the old docker container if existing
if docker container inspect $DOCKER_IMAGE > /dev/null 2>&1; then
    docker container rm $DOCKER_IMAGE > /dev/null
fi
docker create --name $DOCKER_CONTAINER --entrypoint /bin/bash $DOCKER_IMAGE
docker cp -L $DOCKER_CONTAINER:/etc/os-release $TARGET_VERSIONS_PATH/
docker cp -L $DOCKER_CONTAINER:/usr/local/share/buildinfo/pre-versions $TARGET_VERSIONS_PATH/
docker cp -L $DOCKER_CONTAINER:/usr/local/share/buildinfo/post-versions $TARGET_VERSIONS_PATH/
docker container rm $DOCKER_CONTAINER
