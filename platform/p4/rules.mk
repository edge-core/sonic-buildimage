# include $(PLATFORM_PATH)/p4-softswitch.mk
include $(PLATFORM_PATH)/tenjin.mk
include $(PLATFORM_PATH)/p4-hlir.mk
include $(PLATFORM_PATH)/p4c-bm.mk
# include $(PLATFORM_PATH)/p4-sai-bm.mk
include $(PLATFORM_PATH)/p4-bmv.mk
include $(PLATFORM_PATH)/p4-switch.mk
include $(PLATFORM_PATH)/docker-sonic-p4.mk

SONIC_ALL += $(DOCKER_SONIC_P4)

$(LIBSAIREDIS)_DEPENDS += $(P4_SWITCH)
$(LIBSAIREDIS)_RDEPENDS += $(P4_SWITCH)
