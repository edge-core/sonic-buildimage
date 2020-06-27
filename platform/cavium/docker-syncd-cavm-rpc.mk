# docker image for cavium syncd with rpc

DOCKER_SYNCD_CAVM_RPC = docker-syncd-cavm-rpc.gz
$(DOCKER_SYNCD_CAVM_RPC)_PATH = $(PLATFORM_PATH)/docker-syncd-cavm-rpc
$(DOCKER_SYNCD_CAVM_RPC)_DEPENDS += $(SYNCD_RPC) $(LIBTHRIFT) $(CAVM_LIBSAI) $(XP_TOOLS) $(PTF)
$(DOCKER_SYNCD_CAVM_RPC)_FILES += $(SUPERVISOR_PROC_EXIT_LISTENER_SCRIPT)
ifeq ($(INSTALL_DEBUG_TOOLS), y)
$(DOCKER_SYNCD_CAVM_RPC)_DEPENDS += $(SYNCD_RPC_DBG) \
                                    $(LIBSWSSCOMMON_DBG) \
                                    $(LIBSAIMETADATA_DBG) \
                                    $(LIBSAIREDIS_DBG)
endif
$(DOCKER_SYNCD_CAVM_RPC)_LOAD_DOCKERS += $(DOCKER_SYNCD_CAVM)
SONIC_DOCKER_IMAGES += $(DOCKER_SYNCD_CAVM_RPC)
ifeq ($(ENABLE_SYNCD_RPC),y)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_CAVM_RPC)
endif

$(DOCKER_SYNCD_CAVM_RPC)_CONTAINER_NAME = syncd
$(DOCKER_SYNCD_CAVM_RPC)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SYNCD_CAVM_RPC)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SYNCD_CAVM_RPC)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
