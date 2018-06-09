# docker image for virtual switch based sonic docker image

DOCKER_SONIC_VS = docker-sonic-vs.gz
$(DOCKER_SONIC_VS)_PATH = $(PLATFORM_PATH)/docker-sonic-vs
$(DOCKER_SONIC_VS)_DEPENDS += $(SWSS) \
                              $(SYNCD_VS) \
                              $(REDIS_TOOLS) \
                              $(REDIS_SERVER) \
                              $(PYTHON_SWSSCOMMON) \
                              $(LIBTEAMDCT) \
                              $(LIBTEAM_UTILS) \
                              $(SONIC_DEVICE_DATA) \
                              $(SONIC_UTILS) \
                              $(IPROUTE2)

ifeq ($(SONIC_ROUTING_STACK), quagga)
$(DOCKER_SONIC_VS)_DEPENDS += $(QUAGGA)
else ifeq ($(SONIC_ROUTING_STACK), frr)
$(DOCKER_SONIC_VS)_DEPENDS += $(FRR)
else
$(DOCKER_SONIC_VS)_DEPENDS += $(GOBGP)
endif

$(DOCKER_SONIC_VS)_FILES += $(CONFIGDB_LOAD_SCRIPT) \
                            $(ARP_UPDATE_SCRIPT)

$(DOCKER_SONIC_VS)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE)
SONIC_DOCKER_IMAGES += $(DOCKER_SONIC_VS)
