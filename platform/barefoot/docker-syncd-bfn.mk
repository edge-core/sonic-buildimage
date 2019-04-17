# docker image for syncd

DOCKER_SYNCD_BFN = docker-syncd-bfn.gz
$(DOCKER_SYNCD_BFN)_PATH = $(PLATFORM_PATH)/docker-syncd-bfn
$(DOCKER_SYNCD_BFN)_DEPENDS += $(SYNCD)
$(DOCKER_SYNCD_BFN)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE_STRETCH)
SONIC_DOCKER_IMAGES += $(DOCKER_SYNCD_BFN)
SONIC_STRETCH_DOCKERS += $(DOCKER_SYNCD_BFN)
ifneq ($(ENABLE_SYNCD_RPC),y)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_BFN)
endif

$(DOCKER_SYNCD_BFN)_CONTAINER_NAME = syncd
$(DOCKER_SYNCD_BFN)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SYNCD_BFN)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SYNCD_BFN)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
$(DOCKER_SYNCD_BFN)_RUN_OPT += -v /host/warmboot:/var/warmboot
