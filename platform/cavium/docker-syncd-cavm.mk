# docker image for cavium syncd

DOCKER_SYNCD_CAVM = docker-syncd-cavm.gz
$(DOCKER_SYNCD_CAVM)_PATH = $(PLATFORM_PATH)/docker-syncd-cavm
$(DOCKER_SYNCD_CAVM)_DEPENDS += $(SYNCD) $(CAVM_LIBSAI) $(XP_TOOLS)
$(DOCKER_SYNCD_CAVM)_FILES += $(SUPERVISOR_PROC_EXIT_LISTENER_SCRIPT)
ifeq ($(INSTALL_DEBUG_TOOLS), y)
$(DOCKER_SYNCD_CAVM)_DEPENDS += $(SYNCD_DBG) \
                                $(LIBSWSSCOMMON_DBG) \
                                $(LIBSAIMETADATA_DBG) \
                                $(LIBSAIREDIS_DBG)
endif
$(DOCKER_SYNCD_CAVM)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE)
SONIC_DOCKER_IMAGES += $(DOCKER_SYNCD_CAVM)
ifneq ($(ENABLE_SYNCD_RPC),y)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_CAVM)
endif

$(DOCKER_SYNCD_CAVM)_CONTAINER_NAME = syncd
$(DOCKER_SYNCD_CAVM)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SYNCD_CAVM)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SYNCD_CAVM)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
$(DOCKER_SYNCD_CAVM)_BASE_IMAGE_FILES += monit_syncd:/etc/monit/conf.d
