# This is used by the image building script referenced below. Normally it just takes the directory name but in this
# case we want it to be called something else.
IMAGE_NAME=flytekit-python-template
VERSION=$(shell ./version.sh)

# If you're port-forwarding your service or running the sandbox Flyte deployment you can leave this is as is.
# If you want to use a secure channel with ssl enabled, be sure **not** to use the insecure flag.
INSECURE=-i

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

# The Flyte deployment endpoint. Be sure to override using your remote deployment endpoint if applicable.
FLYTE_HOST=localhost:30081

# In order to use fast_register with minio you must port-forward the service to MINIO_ENDPOINT or the default, localhost:9000
MINIO_ENDPOINT=localhost:9000
ifeq ($(origin DISABLE_MINIO), undefined)
	MINIO_PREFIX = FLYTE_AWS_ENDPOINT=http://$(MINIO_ENDPOINT)/ FLYTE_AWS_ACCESS_KEY_ID=minio FLYTE_AWS_SECRET_ACCESS_KEY=miniostorage
else
	MINIO_PREFIX =
endif

# The Flyte project and domain that we want to register under
PROJECT=flyteexamples
DOMAIN=development
# If you want to create a new project, in an environment with flytekit installed run the following:
# flyte-cli register-project -h ${FLYTE_HOST} -i - myflyteproject --name "My Flyte Project" \
#      --description "My very first project getting started on Flyte"


# This specifies where fast-registered code is uploaded to during registration.
# If you're not using the standard minio deployment on flyte sandbox: update this path to something that
#   - you have write access to
#   - flytepropeller can read (depending on the role it uses)
ADDL_DISTRIBUTION_DIR=s3://my-s3-bucket/flyte-fast-distributions

.SILENT: help
.PHONY: help
help:
	echo Available recipes:
	cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' | awk 'BEGIN { FS = ":.*?## " } { cnt++; a[cnt] = $$1; b[cnt] = $$2; if (length($$1) > max) max = length($$1) } END { for (i = 1; i <= cnt; i++) printf "  $(shell tput setaf 6)%-*s$(shell tput setaf 0) %s\n", max, a[i], b[i] }'
	tput sgr0

.PHONY: debug
debug:
	echo "IMAGE NAME ${IMAGE_NAME}"
	echo "FULL IMAGE NAME ${FULL_IMAGE_NAME}"
	echo "VERSION TAG ${VERSION}"
	echo "REGISTRY ${REGISTRY}"

.PHONY: docker_build
docker_build:
	NOPUSH=1 IMAGE_NAME=${IMAGE_NAME} flytekit_build_image.sh ./Dockerfile ${PREFIX}

# The fast register and serialize targets below allow to you rapidly register your updated code with your Flyte deployment.
# Run `make fast_register` to trigger the sequence.
.PHONY: fast_register
fast_register: fast_serialize
	echo ${DISABLE_MINIO}
	echo ${MINIO_PREFIX}
	${MINIO_PREFIX} flyte-cli fast-register-files -h ${FLYTE_HOST} ${INSECURE} -p ${PROJECT} -d ${DOMAIN} \
		--additional-distribution-dir ${ADDL_DISTRIBUTION_DIR} _pb_output/*

.PHONY: fast_serialize
fast_serialize:
	echo ${CURDIR}
	mkdir ${CURDIR}/_pb_output || true
	rm ${CURDIR}/_pb_output/* || true
	pyflyte --pkgs myapp.workflows serialize --in-container-config-path /root/flyte.config --image ghcr.io/flyteorg/flytekit-python-template:latest fast workflows -f _pb_output/

# The register and serialize targets below allow you to upload your code to your Flyte deployment.
# Simply run `make register` to trigger the sequence.
.PHONY: register
register: docker_build serialize
	flyte-cli register-files -h ${FLYTE_HOST} ${INSECURE} -p ${PROJECT} -d ${DOMAIN} -v ${VERSION} ${CURDIR}/_pb_output/*


.PHONY: serialize
serialize:
	echo ${CURDIR}
	rm -rf ${CURDIR}/_pb_output || true
	mkdir ${CURDIR}/_pb_output || true
	pyflyte --pkgs myapp.workflows serialize --in-container-config-path /root/flyte.config --image ${FULL_IMAGE_NAME}:${VERSION} workflows -f _pb_output
