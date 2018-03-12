DOCKER_IMAGE_FILE=$1
REGISTRY_SERVER=$2
REGISTRY_PORT=$3
REGISTRY_USERNAME=$4
REGISTRY_PASSWD=$5
DOCKER_IMAGE_TAG=$6

set -e
docker load < $DOCKER_IMAGE_FILE

## Fetch the Jenkins build number if inside it
[ ${BUILD_NUMBER} ] || {
    echo "No BUILD_NUMBER found, setting to 0."
    BUILD_NUMBER="0"
}

## Prepare tag
docker_image_name=$(basename $DOCKER_IMAGE_FILE | cut -d. -f1)
remote_image_name=$REGISTRY_SERVER:$REGISTRY_PORT/$docker_image_name:$DOCKER_IMAGE_TAG
timestamp="$(date -u +%Y%m%d)"
build_version="${timestamp}.bld-${BUILD_NUMBER}"
build_remote_image_name=$REGISTRY_SERVER:$REGISTRY_PORT/$docker_image_name:$build_version

## Add registry information as tag, so will push as latest
## Add additional tag with build information
docker tag $docker_image_name $remote_image_name
docker tag $docker_image_name $build_remote_image_name

## Login the docker image registry server
## Note: user name and password are passed from command line
docker login -u $REGISTRY_USERNAME -p "$REGISTRY_PASSWD" $REGISTRY_SERVER:$REGISTRY_PORT

## Push image to registry server
## And get the image digest SHA256
echo "Pushing $remote_image_name"
image_sha=$(docker push $remote_image_name | sed -n "s/.*: digest: sha256:\([0-9a-f]*\).*/\\1/p")
docker rmi $remote_image_name || true
echo "Image sha256: $image_sha"
echo "Pushing $build_remote_image_name"
docker push $build_remote_image_name
docker rmi $build_remote_image_name || true
docker rmi $docker_image_name || true
