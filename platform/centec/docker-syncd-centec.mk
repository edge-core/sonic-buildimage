# docker image for centec syncd

DOCKER_SYNCD_CENTEC = docker-syncd-centec.gz
$(DOCKER_SYNCD_CENTEC)_PATH = $(PLATFORM_PATH)/docker-syncd-centec
$(DOCKER_SYNCD_CENTEC)_DEPENDS += $(SYNCD)
$(DOCKER_SYNCD_CENTEC)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE)
SONIC_DOCKER_IMAGES += $(DOCKER_SYNCD_CENTEC)
ifneq ($(ENABLE_SYNCD_RPC),y)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_CENTEC)
endif

$(DOCKER_SYNCD_CENTEC)_CONTAINER_NAME = syncd
$(DOCKER_SYNCD_CENTEC)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SYNCD_CENTEC)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SYNCD_CENTEC)_RUN_OPT += -v /var/run/docker-syncd:/var/run/sswsyncd
$(DOCKER_SYNCD_CENTEC)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
