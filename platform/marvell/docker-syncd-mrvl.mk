# docker image for mrvl syncd

DOCKER_SYNCD_MRVL = docker-syncd-mrvl.gz
$(DOCKER_SYNCD_MRVL)_PATH = $(PLATFORM_PATH)/docker-syncd-mrvl
$(DOCKER_SYNCD_MRVL)_DEPENDS += $(SYNCD) $(MRVL_FPA) $(REDIS_TOOLS)
ifeq ($(INSTALL_DEBUG_TOOLS), y)
$(DOCKER_SYNCD_MRVL)_DEPENDS += $(SYNCD_DBG) \
                                $(LIBSWSSCOMMON_DBG) \
                                $(LIBSAIMETADATA_DBG) \
                                $(LIBSAIREDIS_DBG)
endif
$(DOCKER_SYNCD_MRVL)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE)
SONIC_DOCKER_IMAGES += $(DOCKER_SYNCD_MRVL)
ifneq ($(ENABLE_SYNCD_RPC),y)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_MRVL)
endif

$(DOCKER_SYNCD_MRVL)_CONTAINER_NAME = syncd
$(DOCKER_SYNCD_MRVL)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SYNCD_MRVL)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SYNCD_MRVL)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
