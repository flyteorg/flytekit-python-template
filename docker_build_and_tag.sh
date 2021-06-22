#!/bin/bash

set -ex

# SET the REGISTRY here, where the docker container should be pushed
REGISTRY=""

# SET the appname here
APP_NAME="myapp"

# If you are using git, then this will automatically use the git head as the
# version
VERSION=$(git rev-parse HEAD)

TAG=${APP_NAME}:${VERSION}
if [ -z "${REGISTRY}" ]; then
  echo "No registry set, creating tag ${TAG}"
else
 TAG="${REGISTRY_NAME}/${TAG}"
 echo "Registry set: creating tag ${TAG}"
fi

# Should be run in the folder that has Dockerfile
docker build --tag ${TAG} .
