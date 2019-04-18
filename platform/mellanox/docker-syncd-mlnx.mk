# docker image for mlnx syncd

DOCKER_SYNCD_MLNX = docker-syncd-mlnx.gz
$(DOCKER_SYNCD_MLNX)_PATH = $(PLATFORM_PATH)/docker-syncd-mlnx
$(DOCKER_SYNCD_MLNX)_DEPENDS += $(SYNCD) $(PYTHON_SDK_API)
ifeq ($(INSTALL_DEBUG_TOOLS), y)
$(DOCKER_SYNCD_MLNX)_DEPENDS += $(SYNCD_DBG) \
                                $(LIBSWSSCOMMON_DBG) \
                                $(LIBSAIMETADATA_DBG) \
                                $(LIBSAIREDIS_DBG)
endif
$(DOCKER_SYNCD_MLNX)_PYTHON_DEBS += $(MLNX_SFPD)
$(DOCKER_SYNCD_MLNX)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE_STRETCH)
SONIC_DOCKER_IMAGES += $(DOCKER_SYNCD_MLNX)
SONIC_STRETCH_DOCKERS += $(DOCKER_SYNCD_MLNX)
ifneq ($(ENABLE_SYNCD_RPC),y)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_MLNX)
endif

$(DOCKER_SYNCD_MLNX)_CONTAINER_NAME = syncd
$(DOCKER_SYNCD_MLNX)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SYNCD_MLNX)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SYNCD_MLNX)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
$(DOCKER_SYNCD_MLNX)_RUN_OPT += -v /host/warmboot:/var/warmboot

