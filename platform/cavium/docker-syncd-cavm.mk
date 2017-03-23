# docker image for cavium syncd

DOCKER_SYNCD_CAVM = docker-syncd-cavm.gz
$(DOCKER_SYNCD_CAVM)_PATH = $(PLATFORM_PATH)/docker-syncd-cavm
$(DOCKER_SYNCD_CAVM)_DEPENDS += $(SYNCD) $(CAVM_LIBSAI) $(XP_TOOLS) $(REDIS_TOOLS)
$(DOCKER_SYNCD_CAVM)_LOAD_DOCKERS += $(DOCKER_BASE)
SONIC_DOCKER_IMAGES += $(DOCKER_SYNCD_CAVM)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_CAVM)

$(DOCKER_SYNCD_CAVM)_CONTAINER_NAME = syncd
$(DOCKER_SYNCD_CAVM)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SYNCD_CAVM)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SYNCD_CAVM)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
