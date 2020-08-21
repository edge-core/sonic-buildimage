# SONiC host service package

ifeq ($(INCLUDE_HOST_SERVICE), y)

SONIC_HOST_SERVICE = sonic-host-service_1.0.0_all.deb
$(SONIC_HOST_SERVICE)_SRC_PATH = $(SRC_PATH)/sonic-host-service
SONIC_MAKE_DEBS += $(SONIC_HOST_SERVICE)

endif
