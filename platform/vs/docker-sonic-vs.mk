# docker image for virtual switch based sonic docker image

DOCKER_SONIC_VS = docker-sonic-vs.gz
$(DOCKER_SONIC_VS)_PATH = $(PLATFORM_PATH)/docker-sonic-vs
$(DOCKER_SONIC_VS)_DEPENDS += $(SWSS) \
                              $(SYNCD_VS) \
                              $(PYTHON_SWSSCOMMON) \
                              $(LIBTEAMDCTL) \
                              $(LIBTEAM_UTILS) \
                              $(SONIC_DEVICE_DATA)

$(DOCKER_SONIC_VS)_PYTHON_DEBS += $(SONIC_UTILS)

$(DOCKER_SONIC_VS)_PYTHON_WHEELS += $(SONIC_YANG_MODELS_PY3)
$(DOCKER_SONIC_VS)_PYTHON_WHEELS += $(SONIC_YANG_MGMT_PY)

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
                            $(SONIC_VERSION)

$(DOCKER_SONIC_VS)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE_BUSTER)
SONIC_DOCKER_IMAGES += $(DOCKER_SONIC_VS)
