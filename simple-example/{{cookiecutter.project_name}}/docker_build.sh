#!/bin/bash

set -e

# SET the REGISTRY here, where the docker container should be pushed
REGISTRY=""

# SET the appname here
PROJECT_NAME="spx_prediction"

while getopts p:r:v:y:e:h flag
do
    case "${flag}" in
        p) PROJECT_NAME=${OPTARG};;
        r) REGISTRY=${OPTARG};;
        v) VERSION=${OPTARG};;
        y) PYTHON_VERSION=${OPTARG};;
        h) echo "Usage: ${0} [-h|[-p <project_name>][-r <registry_name>][-v <version>]]"
           echo "  p: PROJECT_NAME for your workflows. Defaults to 'spx_prediction'."
           echo "  r: REGISTRY name where the docker container should be pushed. Defaults to none - localhost"
           echo "  v: VERSION of the build. Defaults to using the current git head SHA"
           echo "  y: PYTHON_VERSION of the build. Default is 3.8"           
           echo "  h: help (this message)"
           exit 1;;
        *) echo "Usage: ${0} [-h|[-p <project_name>][-r <registry_name>][-v <version>]]"
           exit 1;;
    esac
done

echo ${PYTHON_VERSION}

if [ -z "${PYTHON_VERSION}" ]; then
  echo "No python version set, using 3.8 as default"
  PYTHON_VERSION="3.8"
fi


# If you are using git, then this will automatically use the git head as the
# version
if [ -z "${VERSION}" ]; then
  echo "No version set, using git commit head sha as the version"
  VERSION=$(git rev-parse HEAD)
fi

TAG=${PROJECT_NAME}:${VERSION}
if [ -z "${REGISTRY}" ]; then
  echo "No registry set, creating tag ${TAG}"
else
 TAG="${REGISTRY}/${TAG}"
 echo "Registry set: creating tag ${TAG}"
fi

# convert *.ipynb to *.py
if hash jupyter 2>/dev/null; then
    echo "Jupyter found. converting workflows/*.ipython to *.py"
    jupyter nbconvert workflows/*.ipynb --to script
else
    echo "Jupyter not found"
fi

# generate requirements.txt if pipenv were used
if hash pipenv 2>/dev/null;then
    echo "Pipenv found. Generating requirements.txt"
    pipenv run pip freeze > requirements.txt
else
    echo "Pipenv not found"
fi

docker build --tag ${TAG} --build-arg PYTHON_VERSION=${PYTHON_VERSION} .

echo "Docker image built with tag ${TAG}. You can use this image to run pyflyte package."

