###############################################################################
## Wrapper for starting make inside sonic-slave container
###############################################################################

SHELL = /bin/bash

USER := $(shell id -un)
PWD := $(shell pwd)

MAKEFLAGS += -B

DOCKER_RUN := docker run --rm=true --privileged \
    -v $(PWD):/sonic \
    -it sonic-slave-$(USER)

DOCKER_BUILD = docker build --no-cache \
	       --build-arg user=$(USER) \
	       --build-arg uid=$(shell id -u) \
	       --build-arg guid=$(shell id -g) \
	       -t sonic-slave-$(USER) \
	       sonic-slave

.PHONY: sonic-slave-build sonic-slave-bash

.DEFAULT_GOAL :=  all

%::
	@docker inspect --type image sonic-slave-$(USER) &> /dev/null || $(DOCKER_BUILD)
	@$(DOCKER_RUN) make \
	    -C sonic \
	    -f slave.mk \
	    PLATFORM=$(PLATFORM) \
	    $@

sonic-slave-build :
	@$(DOCKER_BUILD)

sonic-slave-bash :
	@$(DOCKER_RUN) bash
