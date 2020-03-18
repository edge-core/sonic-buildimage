# docker image for mrvl syncd with rpc

DOCKER_SYNCD_MRVL_RPC = docker-syncd-mrvl-rpc.gz
$(DOCKER_SYNCD_MRVL_RPC)_PATH = $(PLATFORM_PATH)/docker-syncd-mrvl-rpc
$(DOCKER_SYNCD_MRVL_RPC)_DEPENDS += $(SYNCD_RPC) $(LIBTHRIFT) $(PTF)
$(DOCKER_SYNCD_MRVL_RPC)_FILES += $(SUPERVISOR_PROC_EXIT_LISTENER_SCRIPT)
ifeq ($(INSTALL_DEBUG_TOOLS), y)
$(DOCKER_SYNCD_MRVL_RPC)_DEPENDS += $(SYNCD_RPC_DBG) \
                                    $(LIBSWSSCOMMON_DBG) \
                                    $(LIBSAIMETADATA_DBG) \
                                    $(LIBSAIREDIS_DBG)
endif
$(DOCKER_SYNCD_MRVL_RPC)_LOAD_DOCKERS += $(DOCKER_SYNCD_BASE)
SONIC_DOCKER_IMAGES += $(DOCKER_SYNCD_MRVL_RPC)
SONIC_STRETCH_DOCKERS += $(DOCKER_SYNCD_MRVL_RPC)
ifeq ($(ENABLE_SYNCD_RPC),y)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_MRVL_RPC)
endif

$(DOCKER_SYNCD_MRVL_RPC)_CONTAINER_NAME = syncd
$(DOCKER_SYNCD_MRVL_RPC)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SYNCD_MRVL_RPC)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SYNCD_MRVL_RPC)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
$(DOCKER_SYNCD_MRVL_RPC)_RUN_OPT += -v /host/warmboot:/var/warmboot
