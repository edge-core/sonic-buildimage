###############################################################################
## Wrapper for starting make inside sonic-slave container
###############################################################################

SHELL = /bin/bash

USER := $(shell id -un)
PWD := $(shell pwd)

MAKEFLAGS += -B

SLAVE_TAG = $(shell shasum sonic-slave/Dockerfile | awk '{print substr($$1,0,11);}')
SLAVE_IMAGE = sonic-slave-$(USER)

DOCKER_RUN := docker run --rm=true --privileged \
    -v $(PWD):/sonic \
    -i$(SONIC_SLAVE_TTY)

DOCKER_BUILD = docker build --no-cache \
	       --build-arg user=$(USER) \
	       --build-arg uid=$(shell id -u) \
	       --build-arg guid=$(shell id -g) \
	       --build-arg hostname=$(shell echo $$HOSTNAME) \
	       -t $(SLAVE_IMAGE) \
	       sonic-slave && \
	       docker tag $(SLAVE_IMAGE):latest $(SLAVE_IMAGE):$(SLAVE_TAG)


MGMT_TAG = $(shell shasum sonic-mgmt/Dockerfile | awk '{print substr($$1,0,11);}')
MGMT_IMAGE = sonic-mgmt-$(USER)

DOCKER_MGMT_BUILD = docker build --no-cache \
	       --build-arg user=$(USER) \
	       --build-arg uid=$(shell id -u) \
	       --build-arg guid=$(shell id -g) \
	       --build-arg hostname=$(shell echo $$HOSTNAME) \
	       -t $(MGMT_IMAGE) \
	       sonic-mgmt && \
	       docker tag $(MGMT_IMAGE):latest $(MGMT_IMAGE):$(MGMT_TAG)


.PHONY: sonic-slave-build sonic-slave-bash sonic-mgmt-build

.DEFAULT_GOAL :=  all

%::
	@docker inspect --type image $(SLAVE_IMAGE):$(SLAVE_TAG) &> /dev/null || \
	    { echo Image $(SLAVE_IMAGE):$(SLAVE_TAG) not found. Building... ; \
	    $(DOCKER_BUILD) ; }
	@$(DOCKER_RUN) $(SLAVE_IMAGE):$(SLAVE_TAG) make \
	    -C sonic \
	    -f slave.mk \
	    PLATFORM=$(PLATFORM) \
	    BUILD_NUMBER=$(BUILD_NUMBER) \
	    ENABLE_DHCP_GRAPH_SERVICE=$(ENABLE_DHCP_GRAPH_SERVICE) \
	    PASSWORD=$(PASSWORD) \
	    USERNAME=$(USERNAME) \
	    $@

sonic-slave-build :
	@$(DOCKER_BUILD)

sonic-slave-bash :
	@docker inspect --type image $(SLAVE_IMAGE):$(SLAVE_TAG) &> /dev/null || \
	    { echo Image $(SLAVE_IMAGE):$(SLAVE_TAG) not found. Building... ; \
	    $(DOCKER_BUILD) ; }
	@$(DOCKER_RUN) -t $(SLAVE_IMAGE):$(SLAVE_TAG) bash

sonic-mgmt-build :
	@$(DOCKER_MGMT_BUILD)
