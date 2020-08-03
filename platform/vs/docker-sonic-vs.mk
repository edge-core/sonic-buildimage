# docker image for virtual switch based sonic docker image

DOCKER_SONIC_VS = docker-sonic-vs.gz
$(DOCKER_SONIC_VS)_PATH = $(PLATFORM_PATH)/docker-sonic-vs
$(DOCKER_SONIC_VS)_DEPENDS += $(SWSS) \
                              $(SYNCD_VS) \
                              $(PYTHON_SWSSCOMMON) \
                              $(LIBTEAMDCTL) \
                              $(LIBTEAM_UTILS) \
                              $(SONIC_DEVICE_DATA) \
                              $(LIBYANG) \
                              $(LIBYANG_CPP) \
                              $(LIBYANG_PY2)

$(DOCKER_SONIC_VS)_PYTHON_DEBS += $(SONIC_UTILS)

# swsssdk is a dependency of sonic-py-common
# TODO: sonic-py-common should depend on swsscommon instead
$(DOCKER_SONIC_VS)_PYTHON_WHEELS += $(SWSSSDK_PY2) \
                                    $(SWSSSDK_PY3) \
                                    $(SONIC_PY_COMMON_PY2) \
                                    $(SONIC_PY_COMMON_PY3) \
                                    $(SONIC_YANG_MODELS_PY3) \
                                    $(SONIC_YANG_MGMT_PY)

ifeq ($(INSTALL_DEBUG_TOOLS), y)
$(DOCKER_SONIC_VS)_DEPENDS += $(SWSS_DBG) \
                              $(LIBSWSSCOMMON_DBG) \
                              $(LIBSAIREDIS_DBG) \
                              $(LIBSAIVS_DBG) \
                              $(SYNCD_VS_DBG)
endif

ifeq ($(SONIC_ROUTING_STACK), quagga)
$(DOCKER_SONIC_VS)_DEPENDS += $(QUAGGA)
else ifeq ($(SONIC_ROUTING_STACK), frr)
$(DOCKER_SONIC_VS)_DEPENDS += $(FRR)
else
$(DOCKER_SONIC_VS)_DEPENDS += $(GOBGP)
endif

$(DOCKER_SONIC_VS)_FILES += $(CONFIGDB_LOAD_SCRIPT) \
                            $(ARP_UPDATE_SCRIPT) \
                            $(BUFFERS_CONFIG_TEMPLATE) \
                            $(QOS_CONFIG_TEMPLATE) \
                            $(SONIC_VERSION) \
                            $(RM_CHASSISDB_CONFIG_SCRIPT)

$(DOCKER_SONIC_VS)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE_BUSTER)
SONIC_DOCKER_IMAGES += $(DOCKER_SONIC_VS)
