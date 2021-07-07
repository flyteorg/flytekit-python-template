export REPOSITORY=flytekit-python-template
# The Flyte project and domain that we want to register under
export PROJECT ?= flyteexamples
export DOMAIN ?= development

# This is used by the image building script referenced below. Normally it just takes the directory name but in this
# case we want it to be called something else.
IMAGE_NAME=flytekit-python-template
VERSION=$(shell ./version.sh)

FLYTE_SANDBOX_NAME := flyte-sandbox

.PHONY: update_boilerplate
update_boilerplate:
	@boilerplate/update.sh

ifeq ($(NOPUSH), true)
	NOPUSH=1
endif

define PIP_COMPILE
pip-compile $(1) --upgrade --verbose
endef

# If the REGISTRY environment variable has been set, that means the image name will not just be tagged as
#   flytecookbook:<sha> but rather,
#   docker.io/lyft/flytecookbook:<sha> or whatever your REGISTRY is.
ifneq ($(origin REGISTRY), undefined)
	FULL_IMAGE_NAME = ${REGISTRY}/${IMAGE_NAME}
else
	FULL_IMAGE_NAME = ${IMAGE_NAME}
endif

define RUN_IN_SANDBOX
docker exec -it \
	-e DOCKER_BUILDKIT=1 \
	-e MAKEFLAGS \
	-e REGISTRY \
	-e VERSION \
    -w /root \
	$(FLYTE_SANDBOX_NAME) \
	$(1)
endef

.SILENT: help
.PHONY: help
help:
	echo Available recipes:
	cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' | awk 'BEGIN { FS = ":.*?## " } { cnt++; a[cnt] = $$1; b[cnt] = $$2; if (length($$1) > max) max = length($$1) } END { for (i = 1; i <= cnt; i++) printf "  $(shell tput setaf 6)%-*s$(shell tput setaf 0) %s\n", max, a[i], b[i] }'
	tput sgr0

# Helper to determine if a sandbox is up and running
.PHONY: _requires-sandbox-up
_requires-sandbox-up:
ifeq ($(shell docker ps -f name=$(FLYTE_SANDBOX_NAME) --format={.ID}),)
	$(error Cluster has not been started! Use 'make start' to start a cluster)
endif

.PHONY: debug
debug:
	echo "IMAGE NAME ${IMAGE_NAME}"
	echo "FULL IMAGE NAME ${FULL_IMAGE_NAME}"
	echo "VERSION TAG ${VERSION}"
	echo "REGISTRY ${REGISTRY}"

.PHONY: docker_push
docker_push: docker_build
ifdef REGISTRY
	docker push ${TAGGED_IMAGE}
endif

.PHONY: docker_build
docker_build:
ifdef REGISTRY
	docker build . --tag ${IMAGE_NAME}:${VERSION}
endif
ifndef REGISTRY
	flytectl sandbox exec -- docker build . --tag ${IMAGE_NAME}:${VERSION}
endif

.PHONY: fast_serialize
fast_serialize:
	echo ${CURDIR}
	pyflyte --pkgs myapp.workflows package --image ${IMAGE_NAME}:${VERSION} --fast --force


.PHONY: register
register:
	flytectl register files -p ${PROJECT} -d ${DOMAIN} -v ${VERSION} --archive flyte-package.tgz


.PHONY: serialize
serialize:
	echo ${CURDIR}
	pyflyte --pkgs myapp.workflows package --image ${IMAGE_NAME}:${VERSION} --force

.PHONY: start
start:
	flytectl sandbox start --source=$(shell pwd)

.PHONY: teardown
teardown: _requires-sandbox-up  ## Teardown Flyte sandbox
	flytectl sandbox teardown

.PHONY: status
status: _requires-sandbox-up  ## Show status of Flyte deployment
	kubectl get pods -n flyte
	echo "\n\n"
	flytectl sandbox status

.PHONY: shell
shell: _requires-sandbox-up  ## Drop into a development shell
	$(call PUSH_IF_REGISTRY_EXIST,ls)
