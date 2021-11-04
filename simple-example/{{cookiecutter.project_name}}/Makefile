define LOG
echo "$(shell tput bold)$(shell tput setaf 2)$(1)$(shell tput sgr0)"
endef

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

.PHONY: setup
setup:
	$(call LOG,Starting Flyte sandbox)
	flytectl sandbox start --source=$(shell pwd)

.PHONY: start
start: setup register
	echo "Flyte is ready! Flyte UI is available at http://localhost:$(FLYTE_PROXY_PORT)/console."

.PHONY: register
register: _requires-sandbox-up  ## Register Flyte cookbook workflows
	$(call LOG,Registering example workflows in cookbook/$(EXAMPLES_MODULE))
	$(call RUN_IN_SANDBOX,make -C cookbook/$(EXAMPLES_MODULE) serialize)
	make -C cookbook/$(EXAMPLES_MODULE) register

# Helper to determine if a sandbox is up and running
.PHONY: _requires-sandbox-up
_requires-sandbox-up:
{% raw %}
ifeq ($(shell docker ps -f name=$(FLYTE_SANDBOX_NAME) --format='{{.ID}}'),)
{% endraw %}
	$(error Cluster has not been started! Use 'make start' to start a cluster)
endif
