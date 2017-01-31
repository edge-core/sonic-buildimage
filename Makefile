###############################################################################
## Wrapper for starting make inside sonic-slave container
###############################################################################

SHELL = /bin/bash

USER := $(shell id -un)
PWD := $(shell pwd)

MAKEFLAGS += -B

DOCKER_RUN := docker run --rm=true --privileged \
    -v $(PWD):/sonic \
    -i$(SONIC_SLAVE_TTY)

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
	@$(DOCKER_RUN) sonic-slave-$(USER) make \
	    -C sonic \
	    -f slave.mk \
	    PLATFORM=$(PLATFORM) \
	    SKU=$(SKU) \
	    $@

sonic-slave-build :
	@$(DOCKER_BUILD)

sonic-slave-bash :
	@$(DOCKER_RUN) -t sonic-slave-$(USER) bash
